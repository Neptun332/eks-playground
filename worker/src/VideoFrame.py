from dataclasses import dataclass
from datetime import datetime

import numpy as np


@dataclass(frozen=True)
class VideoFrame:
    frame: np.ndarray
    producer_timestamp: datetime
