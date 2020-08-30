from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE
from socket import socketpair as _socketpair
from types import coroutine


@coroutine
def recv(stream, size):
    # awaitable which waits until something can be read
    print("    recv: waiting for read")
    yield (EVENT_READ, stream)
    print("    recv: reading")
    data = stream.recv(size)
    print("    recv: finished")
    return data


@coroutine
def send(stream, data):
    # awaitable which waits until data can be written
    while data:
        print("    send: waiting for write")
        yield (EVENT_WRITE, stream)
        print("    send: writing")
        size = stream.send(data)
        data = data[size:]
    print("    send: finished")


@coroutine
def socketpair():
    print("    sockets: setting up")
    lhs, rhs = _socketpair()
    lhs.setblocking(False)
    rhs.setblocking(False)
    yield
    print("    sockets: finished")
    return lhs, rhs


async def main():
    print("  main: started")
    lhs, rhs = await socketpair()
    await send(lhs, "hello".encode("utf-8"))
    data = await recv(rhs, 1024)
    text = data.decode("utf-8")
    print(f"  main: received '{text}'")
    lhs.close()
    rhs.close()
    print("  main: finished")


def run_until_complete(task):
    tasks = [(task, None)]

    selector = DefaultSelector()

    while tasks or selector.get_map():
        print("___________________________________")

        # poll I/O and resume when ready
        timeout = 0.0 if tasks else None
        for key, events in selector.select(timeout):
            tasks.append((key.data, None))
            selector.unregister(key.fileobj)

        queue, tasks = tasks, []
        for task, data in queue:
            try:
                print(f"loop: send {data} into {task.__name__}")
                data = task.send(data)
                print(f"loop: received {data} from {task.__name__}")
            except StopIteration as res:
                pass
            except Exception as exp:
                print(repr(exp))
            else:
                if data:
                    req, _ = data
                    if req == EVENT_READ:
                        stream = data[1]
                        selector.register(stream, EVENT_READ, task)
                    elif req == EVENT_WRITE:
                        stream = data[1]
                        selector.register(data[1], EVENT_WRITE, task)
                else:
                    tasks.append((task, None))


if __name__ == "__main__":
    run_until_complete(main())
