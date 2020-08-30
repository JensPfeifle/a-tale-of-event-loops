# implements an event loop which can run a single task to completion

from types import coroutine


@coroutine
def coro():
    print("coro: about to yield")
    yield
    print("coro: back from yield")
    return None  # explicit


async def helloworld(repeat):
    for n in range(repeat):
        print(f"hello: before await {n}")
        await coro()
        print(f"back from await {n}")


def run_until_complete(task):
    try:
        while True:
            print("send it!")
            task.send(None)
            print("received control")
    except StopIteration:
        pass


if __name__ == "__main__":
    hw = helloworld(5)
    run_until_complete(hw)
