from abc import ABC, abstractmethod


class ObservabilityMetrics(ABC):
    @abstractmethod
    def gather_current_metrics(self):
        raise NotImplementedError()

    @abstractmethod
    def reset_metrics(self):
        raise NotImplementedError()
