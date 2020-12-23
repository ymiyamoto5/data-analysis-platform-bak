from typing import List, Iterable, Callable, Any, cast
from asyncio import get_event_loop, Task
from os import cpu_count
from multiprocessing import Pool


async def read_text(fname: str) -> str:
    with open(fname) as fp:
        result = fp.read()
    return result


async def main(fname: str) -> str:
    txt = Task(read_text(fname))
    result = await txt
    return result


def _wrap_async(func: Callable, *args: Any) -> Any:
    loop = get_event_loop()
    result = loop.run_until_complete(func(*args))
    loop.close()
    return result


def pmap_async(func: Callable, arg: Iterable, chunk: int = 2) -> List[Any]:
    with Pool(chunk) as pool:
        result = pool.starmap_async(_wrap_async, [(func, a) for a in arg]).get()
    return result


result = pmap_async(main, ["sample.txt"])
print(result)
