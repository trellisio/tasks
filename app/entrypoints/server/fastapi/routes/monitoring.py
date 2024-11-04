from classy_fastapi import Routable, get
from fastapi import Response
from kink import di, inject
from starlette.status import HTTP_204_NO_CONTENT


@inject()
class MonitoringRoutes(Routable):
    @get("/healthz")
    async def healthz(self):
        return Response(status_code=HTTP_204_NO_CONTENT)


monitoring_routes = di[MonitoringRoutes]
