import asyncio
import concurrent.futures


def print_num(num):
    print(num)


async def async_by_process():
    executor = concurrent.futures.ProcessPoolExecutor()
    queue = asyncio.Queue()

    for i in range(10):
        queue.put_nowait(i)

    async def proc(q):
        while not q.empty():
            i = await q.get()
            future = loop.run_in_executor(executor, print_num, i)
            await future

    tasks = [proc(queue) for i in range(4)]  # 4 = number of cpu core
    return await asyncio.wait(tasks)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_by_process())
