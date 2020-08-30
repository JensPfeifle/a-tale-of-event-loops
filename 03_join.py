# wait for child tasks to complete by using `join`

from collections import defaultdict
from types import coroutine


@coroutine
def coro():
    # a random coroutine
    print("    coro: about to yield")
    yield  # this is where control is handed back to the loop!
    print("    coro: back from yield")
    return None  # explicit


@coroutine
def join(task):
    # awaitable that is notified when a task completes
    result = yield ("join", task)
    if isinstance(result, Exception):
        print(f"    join: got exception {repr(result)}")
        raise result
    return result


@coroutine
def spawn(task):
    # sends a request to spawn a task
    child = yield ("spawn", task)
    # pass child back to parent
    return child


async def helloworld(repeat):
    print("  hello: started")
    # my task, with multiple awaits to break it up
    for n in range(repeat):
        print(f"  hello: before await {n}")
        await coro()
        print(f"  hello: back from await {n}")
    print("  hello: finished")
    return "hello"


async def main():
    # parent task
    print("  main: started")
    child = await spawn(helloworld(5))
    # now we wait for child to finish before exiting
    print("  main: join child")
    result = await join(child)
    print(f"  main: got result {result}")
    print("  main: finished")


def run_until_complete(task):
    # initialize tasks with given task, and data (to send into it) as None
    tasks = [(task, None)]
    # tasks to resume when a task completes
    watch = defaultdict(list)

    # outer loop finishes when all tasks are complete
    while tasks:
        print("___________________________________")
        queue, tasks = tasks, []
        # inner loop = "tick"
        for task, data in queue:
            try:
                print(f"loop: send {data} into {task.__name__}")
                data = task.send(data)
                print(f"loop: received {data} from {task.__name__}")
            except StopIteration as res:
                # task finished
                returnval = res.value
                # schedule tasks which were waiting on this one
                for t in watch[task]:
                    tasks.append((t, returnval))
            except Exception as exp:
                # catch all to prevent loop exit
                print(repr(exp))
                # send exception into tasks which were waiting on this one
                for t in watch[task]:
                    tasks.append((t, exp))
            else:
                if data:
                    req, t = data
                    if req == "spawn":
                        tasks.append((t, None))
                        tasks.append((task, t))
                    elif req == "join":
                        watch[t].append(task)
                else:
                    # reshedule the task
                    tasks.append((task, None))


if __name__ == "__main__":
    run_until_complete(main())
