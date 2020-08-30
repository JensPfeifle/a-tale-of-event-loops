# sleeping and timers

from heapq import heappop, heappush
from time import sleep as _sleep
from timeit import default_timer
from types import coroutine

# global clock
clock = default_timer


@coroutine
def sleep(seconds):
    # awaitable which sleeps for a certain number of seconds
    print("    sleep: about to sleep")
    yield ("sleep", seconds)  # "please reschedule me in n seconds"
    print("    sleep: back from sleep")


async def main():
    print("  main: started")
    await sleep(3)
    print("  main: finished")


def run_until_complete(task):
    tasks = [(task, None)]
    timers = []  # sleeping tasks

    while tasks or timers:
        print("___________________________________")
        if not tasks:
            # sleep until we have to wake the first timer
            _sleep(max(0.0, timers[0][0] - clock()))

        # schedule tasks when their timer has elapsed
        # timers[0] accesses first item of priority queue
        while timers and timers[0][0] < clock():
            _, task = heappop(timers)
            tasks.append((task, None))

        queue, tasks = tasks, []
        for task, data in queue:
            try:
                print(f"loop: send {data} into {task.__name__}")
                data = task.send(data)
                print(f"loop: received {data} from {task.__name__}")
            except StopIteration as res:
                pass
            except Exception as exp:
                # catch all to prevent loop exit
                print(repr(exp))
            else:
                if data:
                    req, _ = data
                    if req == "sleep":
                        delay = data[1]
                        # don't reschedule right away, but set a timer instead
                        heappush(timers, (clock() + delay, task))
                else:
                    # reshedule the task
                    tasks.append((task, None))


if __name__ == "__main__":
    run_until_complete(main())
