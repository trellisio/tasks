from kink import inject

from app.services.ports import ObservabilityMetrics


@inject(alias=ObservabilityMetrics)
class InMemoryMetrics(ObservabilityMetrics):
    def gather_current_metrics(self) -> bytes:  # noqa: PLR6301
        return b""

    def reset_metrics(self) -> None:
        pass
