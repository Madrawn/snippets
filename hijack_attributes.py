from contextlib import contextmanager
globals()["__hijacked_attrs__"] = {}


def hijack_attr(obj, attr, getter, setter):
    """
    Usage example:
    class SomeClass:
        def __init__(self):
            self.some_attr = None


    dict_test = {"test": "different value"}
    some_obj = SomeClass()
    some_obj.some_attr = "value"

    hijack_attr(
        some_obj,
        attr="some_attr",
        getter=lambda obj, key: dict_test["test"],
        setter=lambda obj, key, value: dict_test.update({key: value}),
    )
    """
    globals()["__hijacked_attrs__"][(obj, attr)] = (getter, setter)
    usualget = obj.__class__.__getattribute__

    def sneaky_getter(slf, key):
        if (slf, key) in globals()["__hijacked_attrs__"]:
            getter, _ = globals()["__hijacked_attrs__"][(slf, key)]
            return getter(slf, key)
        return usualget(slf, key)

    obj.__class__.__getattribute__ = sneaky_getter
    usualset = obj.__class__.__setattr__

    def sneaky_setter(slf, key, value):
        if (slf, key) in globals()["__hijacked_attrs__"]:
            _, setter = globals()["__hijacked_attrs__"][(slf, key)]
            setter(slf, key, value)
        else:
            usualset(slf, key, value)

    obj.__class__.__setattr__ = sneaky_setter




@contextmanager
def hijacked_attributes(obj, attr, getter, setter):
    """
    # Usage example
    class MyClass:
        def __init__(self, value):
            self.value = value


    def get_value(obj, attr):
        return "Value has been hijacked!"


    def set_value(obj, attr, value):
        print(f"Trying to set {attr} to {value}, but nope!")


    my_obj = MyClass(10)

    with hijacked_attributes(my_obj, "value", get_value, set_value):
        print(my_obj.value)  # Output: Value has been hijacked!
        my_obj.value = 20  # Output: Trying to set value to 20, but nope!

    print(my_obj.value)  # Output: 10, since the context manager has exited
    """
    # Save the original methods
    original_getattribute = obj.__class__.__getattribute__
    original_setattr = obj.__class__.__setattr__

    # Define the new methods
    def new_getattribute(slf, key):
        if (slf, key) == (obj, attr):
            return getter(slf, key)
        return original_getattribute(slf, key)

    def new_setattr(slf, key, value):
        if (slf, key) == (obj, attr):
            setter(slf, key, value)
        else:
            original_setattr(slf, key, value)

    # Set the new methods
    obj.__class__.__getattribute__ = new_getattribute
    obj.__class__.__setattr__ = new_setattr

    try:
        yield
    finally:
        # Revert to the original methods
        obj.__class__.__getattribute__ = original_getattribute
        obj.__class__.__setattr__ = original_setattr

