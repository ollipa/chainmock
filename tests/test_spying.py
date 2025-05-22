import pytest
from chainmock import mocker, State
from unittest.mock import DEFAULT  # For comparing with spy_expected_return_value initial state if needed

# --- Helper Class Definition ---
class MyClass:
    def __init__(self):
        self._call_count = 0

    def method_to_spy(self, val="default", raise_ex=None):
        self._call_count += 1
        if raise_ex:
            if isinstance(raise_ex, type) and issubclass(raise_ex, BaseException):
                raise raise_ex(f"Test Exception type: {raise_ex.__name__}")
            elif isinstance(raise_ex, BaseException):
                raise raise_ex
        return f"Original method called with {val}"

    def method_returns_value(self, value_to_return):
        self._call_count += 1
        return value_to_return

    def method_raises_ex(self, ex_to_raise):
        self._call_count += 1
        if isinstance(ex_to_raise, type) and issubclass(ex_to_raise, BaseException):
            raise ex_to_raise("Test Exception from method_raises_ex")
        raise ex_to_raise

    @property
    def call_count(self):
        return self._call_count

# --- Test Class for spy(...).return_value(...) ---
class TestSpyReturnValue:

    def test_success_case(self, mocker):
        obj = MyClass()
        EXPECTED_VALUE = "Original method called with test_success"
        # Spy validation expects the original method to return this value
        mocker(obj).spy("method_to_spy").return_value(EXPECTED_VALUE)
        
        actual_return = obj.method_to_spy("test_success")
        assert actual_return == EXPECTED_VALUE
        # Chainmock teardown validation will pass

    def test_failure_wrong_value_returned(self, mocker):
        obj = MyClass()
        # Original method will return "Original method called with actual"
        mocker(obj).spy("method_to_spy").return_value("expected_value")
        
        obj.method_to_spy("actual") # Call the original method
        
        with pytest.raises(AssertionError) as excinfo:
            State.validate_mocks()
        
        assert "Spy for 'MyClass.method_to_spy' expected to return 'expected_value' on call 1" in str(excinfo.value)
        assert "but it returned 'Original method called with actual'" in str(excinfo.value)
        State.reset_state()

    def test_failure_exception_raised_instead_of_value(self, mocker):
        obj = MyClass()
        # Spy validation expects "expected_value"
        mocker(obj).spy("method_to_spy").return_value("expected_value")
        
        with pytest.raises(ValueError, match="Test Exception type: ValueError"): # Original exception
            obj.method_to_spy(raise_ex=ValueError)
            
        with pytest.raises(AssertionError) as excinfo:
            State.validate_mocks()
            
        assert "Spy for 'MyClass.method_to_spy' expected to return 'expected_value' on call 1" in str(excinfo.value)
        assert "but it raised ValueError('Test Exception type: ValueError')" in str(excinfo.value)
        State.reset_state()

    def test_multiple_calls_all_must_return_same_expected_value_success(self, mocker):
        obj = MyClass()
        EXPECTED_VALUE = "Consistent Value"
        # We need method_returns_value to ensure it returns what we expect for validation
        mocker(obj).spy("method_returns_value").return_value(EXPECTED_VALUE)

        ret1 = obj.method_returns_value(EXPECTED_VALUE)
        ret2 = obj.method_returns_value(EXPECTED_VALUE)
        assert ret1 == EXPECTED_VALUE
        assert ret2 == EXPECTED_VALUE
        # Chainmock teardown validation will pass

    def test_multiple_calls_one_returns_wrong_value(self, mocker):
        obj = MyClass()
        EXPECTED_VALUE = "Consistent Value"
        mocker(obj).spy("method_returns_value").return_value(EXPECTED_VALUE)

        obj.method_returns_value(EXPECTED_VALUE)  # Call 1: Correct
        obj.method_returns_value("Wrong Value")   # Call 2: Incorrect

        with pytest.raises(AssertionError) as excinfo:
            State.validate_mocks()
        
        assert f"Spy for 'MyClass.method_returns_value' expected to return {repr(EXPECTED_VALUE)} on call 2" in str(excinfo.value)
        assert f"but it returned 'Wrong Value'" in str(excinfo.value)
        State.reset_state()

    def test_multiple_calls_one_raises_exception(self, mocker):
        obj = MyClass()
        EXPECTED_VALUE = "Consistent Value"
        mocker(obj).spy("method_to_spy").return_value(EXPECTED_VALUE)

        obj.method_to_spy(EXPECTED_VALUE)  # Call 1: Correct (assuming method_to_spy can return its input)
                                          # Let's use method_returns_value for clarity
        
        # Re-setup for clarity
        obj_rv = MyClass() # new instance
        mocker(obj_rv).spy("method_returns_value").return_value(EXPECTED_VALUE)
        obj_rv.method_returns_value(EXPECTED_VALUE) # Call 1: Correct

        # Make the second call raise an exception
        obj_ex_raiser = MyClass() # new instance for the raising part
        mocker(obj_ex_raiser).spy("method_to_spy").return_value(EXPECTED_VALUE) # Spy on a different method or ensure context
        
        # This test setup is tricky. If we use the same spy instance for both calls,
        # the first call to method_returns_value sets up an expectation.
        # If the *second* call is to a *different method or configuration* that raises,
        # it doesn't directly violate the *first* spy's return_value expectation for its *own* calls.
        # The `_spy_actual_outcomes` list is per-spy.
        # Let's refine the test object:
        class MultiCallClass:
            def __init__(self): self.calls = 0
            def method(self, val_to_return, raise_ex=None):
                self.calls += 1
                if raise_ex and self.calls == 2:
                    if isinstance(raise_ex, type): raise raise_ex("Raised on 2nd")
                    raise raise_ex
                return val_to_return
        
        multi_obj = MultiCallClass()
        mocker(multi_obj).spy("method").return_value(EXPECTED_VALUE)

        multi_obj.method(EXPECTED_VALUE) # Call 1, returns EXPECTED_VALUE
        with pytest.raises(TypeError, match="Raised on 2nd"):
            multi_obj.method(EXPECTED_VALUE, raise_ex=TypeError) # Call 2, raises

        with pytest.raises(AssertionError) as excinfo:
            State.validate_mocks()

        assert f"Spy for 'MultiCallClass.method' expected to return {repr(EXPECTED_VALUE)} on call 2" in str(excinfo.value)
        assert "but it raised TypeError('Raised on 2nd')" in str(excinfo.value)
        State.reset_state()


# --- Test Class for spy(...).side_effect(...) ---
class TestSpySideEffect:

    # --- Single Effect Scenarios ---
    def test_single_return_value_success(self, mocker):
        obj = MyClass()
        # The spied method must actually return "SideEffect Value A"
        mocker(obj).spy("method_returns_value").side_effect("SideEffect Value A")
        actual = obj.method_returns_value("SideEffect Value A")
        assert actual == "SideEffect Value A"
        # Validation at teardown

    def test_single_return_value_failure_wrong_value(self, mocker):
        obj = MyClass()
        # method_returns_value will return "Actual Value"
        mocker(obj).spy("method_returns_value").side_effect("Expected SideEffect Value")
        obj.method_returns_value("Actual Value")

        with pytest.raises(AssertionError) as excinfo:
            State.validate_mocks()
        assert "Spy for 'MyClass.method_returns_value' expected to return 'Expected SideEffect Value' on call 1" in str(excinfo.value)
        assert "but it returned 'Actual Value'" in str(excinfo.value)
        State.reset_state()

    def test_single_exception_instance_success(self, mocker):
        obj = MyClass()
        ex_instance = ValueError("foo test instance")
        mocker(obj).spy("method_raises_ex").side_effect(ex_instance)
        
        with pytest.raises(ValueError, match="foo test instance"):
            obj.method_raises_ex(ex_instance)
        # Validation at teardown

    def test_single_exception_instance_failure_returns_value(self, mocker):
        obj = MyClass()
        mocker(obj).spy("method_returns_value").side_effect(ValueError("foo test"))
        obj.method_returns_value("I returned instead") # Doesn't raise

        with pytest.raises(AssertionError) as excinfo:
            State.validate_mocks()
        assert "Spy for 'MyClass.method_returns_value' expected to raise ValueError('foo test') on call 1" in str(excinfo.value)
        assert "but it returned 'I returned instead'" in str(excinfo.value)
        State.reset_state()

    def test_single_exception_instance_failure_different_exception(self, mocker):
        obj = MyClass()
        mocker(obj).spy("method_raises_ex").side_effect(ValueError("Expected this"))

        with pytest.raises(TypeError, match="Test Exception from method_raises_ex"): # Original exception
            obj.method_raises_ex(TypeError) # Raises TypeError

        with pytest.raises(AssertionError) as excinfo:
            State.validate_mocks()
        assert "Spy for 'MyClass.method_raises_ex' expected to raise ValueError('Expected this') on call 1" in str(excinfo.value)
        assert "but it raised TypeError('Test Exception from method_raises_ex')" in str(excinfo.value)
        State.reset_state()

    def test_single_exception_instance_failure_same_type_diff_message(self, mocker):
        obj = MyClass()
        mocker(obj).spy("method_raises_ex").side_effect(ValueError("Expected message"))

        with pytest.raises(ValueError, match="Actual message"): # Original exception
            obj.method_raises_ex(ValueError("Actual message"))

        with pytest.raises(AssertionError) as excinfo:
            State.validate_mocks()
        assert "Spy for 'MyClass.method_raises_ex' expected to raise ValueError('Expected message') on call 1" in str(excinfo.value)
        assert "but it raised ValueError('Actual message')" in str(excinfo.value)
        State.reset_state()

    def test_single_exception_class_success(self, mocker):
        obj = MyClass()
        mocker(obj).spy("method_raises_ex").side_effect(RuntimeError)
        
        with pytest.raises(RuntimeError, match="Test Exception from method_raises_ex"):
            obj.method_raises_ex(RuntimeError)
        # Validation at teardown

    def test_single_exception_class_failure_returns_value(self, mocker):
        obj = MyClass()
        mocker(obj).spy("method_returns_value").side_effect(ValueError)
        obj.method_returns_value("I returned instead")

        with pytest.raises(AssertionError) as excinfo:
            State.validate_mocks()
        assert "Spy for 'MyClass.method_returns_value' expected to raise an instance of ValueError on call 1" in str(excinfo.value)
        assert "but it returned 'I returned instead'" in str(excinfo.value)
        State.reset_state()

    def test_single_exception_class_failure_different_exception(self, mocker):
        obj = MyClass()
        mocker(obj).spy("method_raises_ex").side_effect(ValueError)

        with pytest.raises(TypeError, match="Test Exception from method_raises_ex"): # Original exception
            obj.method_raises_ex(TypeError)

        with pytest.raises(AssertionError) as excinfo:
            State.validate_mocks()
        assert "Spy for 'MyClass.method_raises_ex' expected to raise an instance of ValueError on call 1" in str(excinfo.value)
        assert "but it raised TypeError('Test Exception from method_raises_ex')" in str(excinfo.value)
        State.reset_state()

    # --- Iterable Effects Scenarios ---
    def test_iterable_return_values_success(self, mocker):
        class IterableReturner:
            def __init__(self): self.idx = 0; self.returns = ["Value A", "Value B"]
            def method(self): v = self.returns[self.idx]; self.idx+=1; return v
        obj = IterableReturner()
        mocker(obj).spy("method").side_effect(["Value A", "Value B"])
        
        assert obj.method() == "Value A"
        assert obj.method() == "Value B"
        # Validation at teardown

    def test_iterable_return_values_failure_wrong_value(self, mocker):
        class IterableReturnerWrong:
            def __init__(self): self.idx = 0; self.returns = ["Value A", "Value C_Wrong"]
            def method(self): v = self.returns[self.idx]; self.idx+=1; return v
        obj = IterableReturnerWrong()
        mocker(obj).spy("method").side_effect(["Value A", "Value B_Expected"])

        obj.method() # Returns "Value A" - matches
        obj.method() # Returns "Value C_Wrong" - mismatch

        with pytest.raises(AssertionError) as excinfo:
            State.validate_mocks()
        assert "Spy for 'IterableReturnerWrong.method' expected to return 'Value B_Expected' on call 2" in str(excinfo.value)
        assert "but it returned 'Value C_Wrong'" in str(excinfo.value)
        State.reset_state()

    def test_iterable_exceptions_success(self, mocker):
        class IterableExceptionRaiser:
            def __init__(self): self.idx = 0; self.excs = [ValueError("foo"), TypeError("bar")]
            def method(self): ex = self.excs[self.idx]; self.idx+=1; raise ex
        obj = IterableExceptionRaiser()
        mocker(obj).spy("method").side_effect([ValueError("foo"), TypeError("bar")])
        
        with pytest.raises(ValueError, match="foo"): obj.method()
        with pytest.raises(TypeError, match="bar"): obj.method()
        # Validation at teardown

    def test_iterable_exceptions_failure_wrong_exception(self, mocker):
        class IterableExceptionRaiserWrong:
            def __init__(self): self.idx = 0; self.excs = [ValueError("foo"), ValueError("baz_wrong")]
            def method(self): ex = self.excs[self.idx]; self.idx+=1; raise ex
        obj = IterableExceptionRaiserWrong()
        mocker(obj).spy("method").side_effect([ValueError("foo"), TypeError("bar_expected")])

        with pytest.raises(ValueError, match="foo"): obj.method()
        with pytest.raises(ValueError, match="baz_wrong"): obj.method() # Original exception

        with pytest.raises(AssertionError) as excinfo:
            State.validate_mocks()
        assert "Spy for 'IterableExceptionRaiserWrong.method' expected to raise TypeError('bar_expected') on call 2" in str(excinfo.value)
        assert "but it raised ValueError('baz_wrong')" in str(excinfo.value)
        State.reset_state()

    def test_iterable_mixed_success(self, mocker):
        class IterableMixed:
            def __init__(self): 
                self.idx = 0
                self.effects = ["Value A", ValueError("foo"), "Value B"]
            def method(self): 
                effect = self.effects[self.idx]; self.idx+=1
                if isinstance(effect, BaseException): raise effect
                return effect
        obj = IterableMixed()
        mocker(obj).spy("method").side_effect(["Value A", ValueError("foo"), "Value B"])

        assert obj.method() == "Value A"
        with pytest.raises(ValueError, match="foo"): obj.method()
        assert obj.method() == "Value B"
        # Validation at teardown

    def test_iterable_too_few_calls(self, mocker):
        class CalledOnce:
            def method(self): return "Value A"
        obj = CalledOnce()
        mocker(obj).spy("method").side_effect(["Value A", "Value B"])
        obj.method() # Returns "Value A"

        with pytest.raises(AssertionError) as excinfo:
            State.validate_mocks()
        assert "Spy for 'CalledOnce.method' was called fewer times (1) than expected side effects were provided. 1 expected effect(s) were not consumed, starting with 'Value B'." in str(excinfo.value)
        State.reset_state()

    def test_iterable_too_many_calls(self, mocker):
        class CalledTwice:
            def __init__(self): self.idx = 0
            def method(self): 
                self.idx+=1; 
                if self.idx == 1: return "Value A"
                return "Unexpected Call" 
        obj = CalledTwice()
        mocker(obj).spy("method").side_effect(["Value A"])
        obj.method() # Returns "Value A"
        obj.method() # "Unexpected Call" - beyond defined side_effects

        with pytest.raises(AssertionError) as excinfo:
            State.validate_mocks()
        assert "Spy for 'CalledTwice.method' was called more times (2) than expected side effects were provided (1)." in str(excinfo.value)
        State.reset_state()

# --- General Spy Behavior ---
class TestGeneralSpyBehavior:

    def test_original_method_functionality_preserved(self, mocker):
        obj = MyClass()
        # No .return_value or .side_effect for spy validation.
        # Just spy and check original behavior.
        mocker(obj).spy("method_to_spy") 
        
        assert obj.call_count == 0
        return_val = obj.method_to_spy("test_val")
        assert return_val == "Original method called with test_val"
        assert obj.call_count == 1
        
        with pytest.raises(RuntimeError, match="Test Exception type: RuntimeError"):
            obj.method_to_spy(raise_ex=RuntimeError)
        assert obj.call_count == 2
        # Validation at teardown (should pass as no specific outcomes were expected for spy)

    def test_other_assertions_work_with_return_value(self, mocker):
        obj = MyClass()
        EXPECTED_RETURN = "Original method called with arg1"
        mocker(obj).spy("method_to_spy").return_value(EXPECTED_RETURN).called_once_with("arg1")
        
        actual_return = obj.method_to_spy("arg1")
        assert actual_return == EXPECTED_RETURN
        # Validation at teardown

    def test_other_assertions_work_with_side_effect_value(self, mocker):
        obj = MyClass()
        EXPECTED_SE_RETURN = "Original method called with arg_se"
        mocker(obj).spy("method_to_spy").side_effect(EXPECTED_SE_RETURN).called_once_with("arg_se")

        actual_return = obj.method_to_spy("arg_se")
        assert actual_return == EXPECTED_SE_RETURN
        # Validation at teardown

    def test_other_assertions_work_with_side_effect_exception(self, mocker):
        obj = MyClass()
        ex_to_raise = RuntimeError("SE Exception")
        mocker(obj).spy("method_to_spy").side_effect(ex_to_raise).called_once_with("arg_ex_se")

        with pytest.raises(RuntimeError, match="SE Exception") as e_info:
            obj.method_to_spy("arg_ex_se", raise_ex=ex_to_raise)
        assert e_info.value.args == ex_to_raise.args # Ensure it's the same exception
        # Validation at teardown

    def test_spy_return_value_with_call_count_success(self, mocker):
        obj = MyClass()
        EXPECTED_VALUE = "Original method called with call_count_val"
        mocker(obj).spy("method_to_spy").return_value(EXPECTED_VALUE).call_count(2)
        
        obj.method_to_spy("call_count_val")
        obj.method_to_spy("call_count_val")
        # Validation at teardown

    def test_spy_return_value_with_call_count_failure_assertion(self, mocker):
        obj = MyClass()
        EXPECTED_VALUE = "Original method called with val"
        # Spy return_value validation will pass for the first call
        mocker(obj).spy("method_to_spy").return_value(EXPECTED_VALUE).call_count(2)
        obj.method_to_spy("val") # Called once

        with pytest.raises(AssertionError) as excinfo:
            State.validate_mocks()
        
        # The error message for call_count from standard assertion logic
        assert "Expected 'MyClass.method_to_spy' to have been called twice. Called once." in str(excinfo.value)
        State.reset_state()

    def test_spy_side_effect_iterable_with_call_count_success(self, mocker):
        class SECCSuccess:
            def __init__(self): self.idx = 0; self.effects = ["SECC1", "SECC2"]
            def method(self): v = self.effects[self.idx]; self.idx+=1; return v
        obj = SECCSuccess()
        mocker(obj).spy("method").side_effect(["SECC1", "SECC2"]).call_count(2)
        obj.method()
        obj.method()
        # Validation at teardown

    def test_spy_side_effect_iterable_call_count_fail_too_few_spy_effects(self, mocker):
        class SECCFailSpyLess:
            def method(self): return "val"
        obj = SECCFailSpyLess()
        # Spy expects 2 side_effects, call_count(1) is also set.
        # Spy validation for too few calls for side_effects should trigger first.
        mocker(obj).spy("method").side_effect(["eff1", "eff2"]).call_count(1) 
        obj.method()

        with pytest.raises(AssertionError) as excinfo:
            State.validate_mocks()
        assert "Spy for 'SECCFailSpyLess.method' was called fewer times (1) than expected side effects were provided. 1 expected effect(s) were not consumed, starting with 'eff2'." in str(excinfo.value)
        State.reset_state()

    def test_spy_side_effect_iterable_call_count_fail_too_many_spy_effects(self, mocker):
        class SECCFailSpyMany:
             def __init__(self): self.idx = 0
             def method(self): self.idx += 1; return f"val{self.idx}"
        obj = SECCFailSpyMany()
        # Spy expects 1 side_effect, call_count(2) is also set.
        # Spy validation for too many calls for side_effects should trigger first.
        mocker(obj).spy("method").side_effect(["eff1"]).call_count(2) 
        obj.method()
        obj.method() # Second call

        with pytest.raises(AssertionError) as excinfo:
            State.validate_mocks()
        assert "Spy for 'SECCFailSpyMany.method' was called more times (2) than expected side effects were provided (1)." in str(excinfo.value)
        State.reset_state()

    def test_spy_side_effect_iterable_call_count_fail_regular_assertion(self, mocker):
        class SECCFailRegular:
            def method(self): return "val"
        obj = SECCFailRegular()
        # Spy side_effect(["val"]) is fine for one call. call_count(2) assertion will fail.
        mocker(obj).spy("method").side_effect(["val"]).call_count(2) 
        obj.method() # Called once

        with pytest.raises(AssertionError) as excinfo:
            State.validate_mocks()
        assert "Expected 'SECCFailRegular.method' to have been called twice. Called once." in str(excinfo.value)
        State.reset_state()

# Note: The chainmock pytest plugin ('mocker' fixture) should generally handle State.validate_mocks()
# and State.reset_state() during test teardown. Manual calls are included in failure tests
# to precisely check the assertion messages. If the plugin is active, these manual calls
# might be redundant for simple pass/fail but are useful for message verification.
# The tests for "success" rely on the plugin's automatic validation at teardown.
# The key for spy().return_value() and spy().side_effect() tests is that the *original spied method*
# must produce the outcomes that these spy configurations are set to validate against.
# They do *not* alter the original method's behavior, only assert its outcome.The file `tests/test_spying.py` has been successfully created/overwritten with the comprehensive test suite.

The tests cover various scenarios for `spy(...).return_value(...)` and `spy(...).side_effect(...)`, including:
*   Success cases where the original method's behavior matches the spy's expectations.
*   Failure cases for mismatched return values.
*   Failure cases where exceptions are raised instead of values, or vice-versa.
*   Failure cases for mismatched exception types or messages.
*   Scenarios with multiple calls, checking if all calls meet the `return_value` expectation.
*   Scenarios for single side effects (return value, exception instance, exception class) and their success/failure modes.
*   Scenarios for iterable side effects (return values, exceptions, mixed) and their success/failure modes.
*   Handling of call count mismatches with iterable side effects (too few or too many calls).
*   Verification that original method functionality is preserved when spied.
*   Confirmation that other assertions (like `called_once_with`, `call_count`) work in conjunction with spy outcome validation.

The helper class `MyClass` and other ad-hoc classes within tests are designed to produce specific outcomes required to validate the spy's new validation logic. Manual `State.validate_mocks()` and `State.reset_state()` are used in failure-checking tests to inspect assertion messages, while success tests rely on the chainmock pytest plugin's teardown validation.
