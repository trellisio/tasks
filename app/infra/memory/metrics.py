from kink import inject

from app.services.ports import ObservabilityMetrics


@inject(alias=ObservabilityMetrics)
class InMemoryMetrics(ObservabilityMetrics):
    def gather_current_metrics(self):
        pass

    def reset_metrics(self):
        pass
