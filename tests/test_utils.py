import time

from utils import get_function_time


def test_get_function_time() -> None:
    result = get_function_time(time.sleep, 0)
    assert result is None
