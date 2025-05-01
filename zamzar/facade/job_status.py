from enum import Enum


class JobStatus(Enum):
    """Enum for the status of a job."""
    INITIALISING = "initialising"
    CONVERTING = "converting"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    CANCELLED = "cancelled"
