import logging
import gc
import time
from pipeline_logger import setup_logger

logger = setup_logger(__name__)


def get_function_time(func, *args, **kwargs):
    gc.disable()
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed_time = time.perf_counter() - start_time
    gc.enable()
    logger.info(f"[{func.__name__}] Execution Time: {elapsed_time:.6f} seconds")
    return result
