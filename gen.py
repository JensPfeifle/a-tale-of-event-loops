# This code shows how values can be passed through mutliple layers of the call
# stack using yield from


def bottom():
    # Returning the yield lets the value that goes up the call stack to come right back
    # down.
    print("bottom >>>")
    tmp = yield 42
    print("<<< bottom")
    return tmp  # ~ raise StopIteration(value=tmp)


def middle():
    print("middle >>>")
    tmp = yield from bottom()
    print("<<< middle")
    return tmp


def top():
    print("top >>>")
    tmp = yield from middle()
    print("<<< top	")
    return tmp


# Get the generator.
gen = top()
value = next(gen)
print(value)  # Prints '42'.
try:
    value = gen.send(4242)
except StopIteration as exc:
    value = exc.value
print(value)  # Prints '4242'.
