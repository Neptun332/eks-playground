import random
from time import sleep
from typing import Any

import numpy as np


class EndpointClientMock:

    def __init__(self, request_time_in_seconds: float):
        self.request_time_in_seconds = request_time_in_seconds

    def get_results(self, payload: Any) -> np.ndarray:
        sleep(self.request_time_in_seconds)
        number_of_records = random.randint(0, 4)
        return np.random.rand(number_of_records, 4)
