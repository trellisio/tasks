from kink import inject
from prometheus_client import generate_latest

from app.services.ports import ObservabilityMetrics


@inject(alias=ObservabilityMetrics)
class PrometheusMetrics(ObservabilityMetrics):
    def gather_current_metrics(self) -> bytes:  # noqa: PLR6301
        return generate_latest()

    def reset_metrics(self) -> None:
        pass
