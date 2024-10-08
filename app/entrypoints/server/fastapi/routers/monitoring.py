from classy_fastapi import Routable, get
from fastapi import Response
from kink import di, inject
from starlette.status import HTTP_204_NO_CONTENT

from app.services.ports import ObservabilityMetrics


@inject()
class MonitoringRoutes(Routable):
    metrics: ObservabilityMetrics

    def __init__(self, metrics: ObservabilityMetrics):
        super().__init__()
        self.metrics = metrics

    @get("/healthz")
    async def healthz(self):
        return Response(status_code=HTTP_204_NO_CONTENT)

    @get("/metrics")
    async def metrics_collector(self):
        metrics = self.metrics.gather_current_metrics()
        self.metrics.reset_metrics()  # reset temporary metrics
        return Response(
            content=metrics, media_type="text/plain; version=0.0.4; charset=utf-8"
        )


monitoring_routes = di[MonitoringRoutes]
