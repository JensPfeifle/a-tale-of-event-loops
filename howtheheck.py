# https://snarky.ca/how-the-heck-does-async-await-work-in-python-3-5/
# important note: this represents the state as of Python 3.5
# for differences between native and generator-based coroutines, see PEP 492
# see also PEP 525

from types import coroutine

# basically, yield from and await are the same
# yield from and await both accept generators, but
#   yield from accepts any generator (including coroutines)
#   await only accepts awaitable objects (which coroutines are)
#     an awaitable object is either a coroutine or defines __await()__
#       __await__() returns an iterator which is not a coroutine

# this generator is marked as a coroutine
@coroutine
def coro():
    print("coro: about to yield")
    yield
    print("coro: back from yield")
    return None  # explicit


# this is an async function, which returns a native coroutine
# you cannot use yield, only await (or return)
# this is so that the interpeter can warn you if you
# try to use coroutines as generators and vice-versa
async def helloworld(repeat):
    for n in range(repeat):
        print(f"hello: before await {n}")
        await coro()
        print(f"back from await {n}")


if __name__ == "__main__":
    hw = helloworld(5)
    hw.send(None)
    try:
        while True:
            print("send it!")
            hw.send(None)
            print("received control")
    except StopIteration:
        pass
