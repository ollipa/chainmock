# Mocking

Chainmock provides a powerful mocking API that allows you to mock methods, properties, and attributes of objects. You can mock any object, including classes, instances, and modules. Chainmock also supports partial mocking and spying of objects.

Partial mocking and spying of objects, allows you to mock or spy only specific methods or attributes of an object. This is useful when you want to mock or spy only a single method of an object, while leaving the rest of the object's behavior intact.

If `mocker` is invoked with an object (eg. class, instance, module), the named members of the object can be mocked or spied individually. For example, by calling `mocker(SomeClass)` you are setting the mocking target to a class. The original object is not modified until you explicitly spy or mock it's members.

_Partially mock_ the `Teapot` class:

```python
#! remove-prefix
>>> # First let's fill a teapot and boil the water without mocking
>>> teapot = Teapot()
>>> assert teapot.state == "empty"
>>> teapot.fill()
>>> assert teapot.state == "full"
>>> teapot.boil()
>>> assert teapot.state == "boiling"

```

```python
#! remove-prefix
>>> # Now let's try the same thing but also mock the boil call
>>> mocker(Teapot).mock("boil")
<chainmock._api.Assert object at ...>
>>> teapot = Teapot()
>>> assert teapot.state == "empty"
>>> teapot.fill()  # fill still works because only boil method is mocked
>>> assert teapot.state == "full"
>>> teapot.boil()  # state is not updated because boil method is mocked
>>> assert teapot.state == "full"
>>> State.teardown() #! hidden

```

!!! note

    For more information, please see also [API reference](../api_reference.md). It contains more examples and extensive documentation about every method and function available in Chainmock.
