"""
event loop to run multiple tasks, needs to handle:
  - driving tasks (and children, recursively) to finish
  - handle any errors in tasks
  - scheduling (round-robin)

"""
from inspect import iscoroutine
from types import coroutine


@coroutine
def spawn(task):
    # sends a request to spawn a task
    yield task


@coroutine
def coro():
    # a random coroutine
    print("    coro: about to yield")
    yield  # this is where control is handed back to the loop!
    print("    coro: back from yield")
    return None  # explicit


async def helloworld(repeat):
    print("  hello: started")
    # my task, with multiple awaits to break it up
    for n in range(repeat):
        print(f"  hello: before await {n}")
        await coro()
        print(f"  hello: back from await {n}")
    print("  hello: finished")


async def main():
    # parent task
    print("  main: started")
    await spawn(helloworld(5))
    print("  main: finished")


def run_until_complete(task):
    # initialize tasks with given task, and data (to send into it) as None
    tasks = [(task, None)]

    # outer loop finishes when all tasks are complete
    while tasks:
        print("___________________________________")
        print(f"loop: sheduled tasks {[t.__name__ for t,d in tasks]}")
        queue = tasks  # tasks to run in this loop iteration
        tasks = []  # gather tasks for next iteration
        # inner loop = "tick"
        for task, data in queue:
            try:
                print(f"loop: send {data} into {task.__name__}")
                data = task.send(data)
                print(f"loop: received {data} from {task.__name__}")
            except StopIteration:
                pass
            except Exception as exp:
                # catch all to prevent loop exit
                print(exp)
            else:
                # if the task returns a coroutine, schedule it
                if iscoroutine(data):
                    tasks.append((data, None))
                # reshedule the parent task
                tasks.append((task, None))


if __name__ == "__main__":
    run_until_complete(main())
