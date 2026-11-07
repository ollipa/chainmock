#!/usr/bin/env python3
"""Bump, release and verify chainmock versions.

The version is stored in pyproject.toml (and mirrored in uv.lock), and each release has a
section in CHANGELOG.md. This script keeps those in sync. See CONTRIBUTING.md for the release
process.
"""
# ruff: noqa: S603, S607

import argparse
import re
import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = ROOT / "pyproject.toml"
LOCKFILE = ROOT / "uv.lock"
CHANGELOG = ROOT / "CHANGELOG.md"
VERSION_FILES = [PYPROJECT, LOCKFILE, CHANGELOG]
MAIN_BRANCH = "main"
GITHUB_REPO = "ollipa/chainmock"
ORIGIN_URL = re.compile(rf"(?:git@github\.com:|https://github\.com/){GITHUB_REPO}(?:\.git)?")

UNRELEASED = "## Unreleased"
# The changelog has other level two headings, so match release headings only.
SECTION_BOUNDARY = re.compile(r"^## (?:Unreleased|Release )", re.MULTILINE)


def read_version() -> str:
    """Read the project version from pyproject.toml."""
    with PYPROJECT.open("rb") as file:
        version = tomllib.load(file)["project"]["version"]
    parse_version(version)
    return version


def changelog_section(heading: str) -> str:
    """Return the body of a changelog section, excluding the heading."""
    text = CHANGELOG.read_text(encoding="utf-8")
    match = re.search(rf"^{re.escape(heading)}$", text, re.MULTILINE)
    if match is None:
        raise SystemExit(f"Section '{heading}' not found in {CHANGELOG.name}.")
    boundary = SECTION_BOUNDARY.search(text, match.end())
    end = boundary.start() if boundary else len(text)
    return text[match.end() : end].strip()


def parse_version(version: str) -> tuple[int, int, int]:
    """Parse a X.Y.Z version into a tuple of integers."""
    match = re.fullmatch(r"([0-9]+)\.([0-9]+)\.([0-9]+)", version)
    if match is None:
        raise SystemExit(f"Invalid version '{version}'. Expected format: X.Y.Z")
    major, minor, patch = (int(part) for part in match.groups())
    return major, minor, patch


def next_version(current: str, bump: str) -> str:
    """Return the version that follows the current version for the given bump."""
    major, minor, patch = parse_version(current)
    if bump == "major":
        return f"{major + 1}.0.0"
    if bump == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def run(*args: str) -> str:
    """Run a command in the repository root and return its standard output."""
    return subprocess.run(
        args, cwd=ROOT, check=True, text=True, stdout=subprocess.PIPE
    ).stdout.strip()


def confirm(question: str) -> bool:
    """Ask the user a yes or no question."""
    try:
        return input(f"{question} [y/N] ").strip().lower() in {"y", "yes"}
    except (EOFError, KeyboardInterrupt):
        print()
        return False


def ensure_gh_authenticated() -> None:
    """Check that GitHub CLI is installed and logged in."""
    try:
        subprocess.run(
            ["gh", "auth", "status", "--hostname", "github.com"],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
    except FileNotFoundError as error:
        raise SystemExit("GitHub CLI (gh) is not installed.") from error
    except subprocess.CalledProcessError as error:
        raise SystemExit("GitHub CLI is not logged in. Run: gh auth login") from error


def ensure_clean_main_branch() -> str:
    """Check that the main branch is checked out, clean and up to date, and return HEAD."""
    origin = run("git", "config", "--get", "remote.origin.url")
    if not ORIGIN_URL.fullmatch(origin):
        raise SystemExit(f"Remote 'origin' must be {GITHUB_REPO} on GitHub (is '{origin}').")
    branch = run("git", "branch", "--show-current")
    if branch != MAIN_BRANCH:
        raise SystemExit(f"Check out the '{MAIN_BRANCH}' branch first (currently on '{branch}').")
    if run("git", "status", "--porcelain"):
        raise SystemExit("The working tree has uncommitted changes.")
    run("git", "fetch", "--quiet", "origin", MAIN_BRANCH)
    head = run("git", "rev-parse", "HEAD")
    if head != run("git", "rev-parse", f"refs/remotes/origin/{MAIN_BRANCH}"):
        raise SystemExit(f"Local '{MAIN_BRANCH}' is not in sync with 'origin/{MAIN_BRANCH}'.")
    return head


def ensure_tag_free(tag: str) -> None:
    """Check that the release tag does not exist on origin."""
    if run("git", "ls-remote", "--tags", "origin", f"refs/tags/{tag}"):
        raise SystemExit(f"Tag {tag} already exists. Bump to a new version first.")


def check(tag: str | None) -> str:
    """Verify that the version, the changelog and the optional release tag agree."""
    version = read_version()
    if tag is not None and tag != f"v{version}":
        raise SystemExit(f"Version mismatch: release tag is {tag}, expected v{version}.")
    if not changelog_section(f"## Release {version}"):
        raise SystemExit(f"Section '## Release {version}' in {CHANGELOG.name} is empty.")
    print(f"Release metadata is consistent for version {version}.")
    return version


def bump(part: str) -> None:
    """Bump the version, update the changelog, push the commit to main and create the release."""
    ensure_clean_main_branch()
    ensure_gh_authenticated()
    current = read_version()
    version = next_version(current, part)
    if not changelog_section(UNRELEASED):
        raise SystemExit(f"Section '{UNRELEASED}' in {CHANGELOG.name} is empty.")
    ensure_tag_free(f"v{version}")

    print(f"Bumping version: {current} -> {version}")
    try:
        # Updates pyproject.toml and the project's entry in uv.lock.
        run("uv", "version", "--no-sync", version)
    except (subprocess.CalledProcessError, KeyboardInterrupt) as error:
        revert_bump()
        raise SystemExit("Updating the version failed. The changes were reverted.") from error
    text = CHANGELOG.read_text(encoding="utf-8")
    text = text.replace(UNRELEASED, f"{UNRELEASED}\n\n## Release {version}", 1)
    CHANGELOG.write_text(text, encoding="utf-8")
    subprocess.run(["git", "--no-pager", "diff"], cwd=ROOT, check=True)

    if not confirm(f"\nCommit to '{MAIN_BRANCH}' and push it to origin?"):
        revert_bump()
        raise SystemExit("Aborted. The changes were reverted.")

    try:
        run("git", "commit", "--message", f"Release {version}", "--", *map(str, VERSION_FILES))
    except (subprocess.CalledProcessError, KeyboardInterrupt) as error:
        revert_bump()
        raise SystemExit("Committing failed. The changes were reverted.") from error

    push = subprocess.run(
        ["git", "push", "origin", f"refs/heads/{MAIN_BRANCH}:refs/heads/{MAIN_BRANCH}"],
        cwd=ROOT,
        check=False,
    )
    if push.returncode != 0:
        raise SystemExit(
            f"Pushing failed. The release commit is on the local '{MAIN_BRANCH}' branch. Retry "
            f"with\n  git push origin {MAIN_BRANCH}\nand then run: release.py release\n"
            f"or drop the commit with\n  git reset --hard origin/{MAIN_BRANCH}"
        )
    print()
    release()


def revert_bump() -> None:
    """Revert the uncommitted changes of an unfinished bump."""
    files = [str(path) for path in VERSION_FILES]
    subprocess.run(["git", "checkout", "--", *files], cwd=ROOT, check=False, capture_output=True)


def release() -> None:
    """Create the GitHub release for the version on the main branch."""
    head = ensure_clean_main_branch()
    ensure_gh_authenticated()
    version = check(None)
    tag = f"v{version}"
    ensure_tag_free(tag)

    notes = changelog_section(f"## Release {version}")
    print(f"\nRelease notes for {tag}:\n\n{notes}\n")
    if not confirm(f"Create GitHub release {tag} at commit {head}? This starts publishing."):
        raise SystemExit("Aborted. Create the release later with: release.py release")
    subprocess.run(
        [
            "gh",
            "release",
            "create",
            tag,
            "--repo",
            GITHUB_REPO,
            "--target",
            head,
            "--title",
            tag,
            "--notes",
            notes,
        ],
        cwd=ROOT,
        check=True,
    )
    print("\nApprove the deployment in the publish workflow run to upload the release to PyPI.")


def main() -> None:
    """Run the command given on the command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    bump_parser = commands.add_parser(
        "bump", help="bump version, update changelog, push to main and create the release"
    )
    bump_parser.add_argument(
        "part", choices=["major", "minor", "patch"], help="version part to bump"
    )
    commands.add_parser("release", help="create the GitHub release for the current version")
    check_parser = commands.add_parser("check", help="verify version and changelog")
    check_parser.add_argument("--tag", help="release tag to verify, for example v1.2.3")

    args = parser.parse_args()
    try:
        if args.command == "bump":
            bump(args.part)
        elif args.command == "release":
            release()
        else:
            check(args.tag)
    except subprocess.CalledProcessError as error:
        raise SystemExit(f"Command failed: {' '.join(map(str, error.cmd))}") from error


if __name__ == "__main__":
    main()
