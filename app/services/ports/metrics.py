from abc import ABC, abstractmethod


class ObservabilityMetrics(ABC):
    @abstractmethod
    def gather_current_metrics(self) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def reset_metrics(self) -> None:
        raise NotImplementedError
