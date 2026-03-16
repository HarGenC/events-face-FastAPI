from enum import Enum


class SyncStatus(str, Enum):
    PROCESSING = "processing"
    FAILED = "failed"
    SUCCESS = "success"
