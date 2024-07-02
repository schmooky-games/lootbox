from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi_healthcheck import HealthCheckFactory, healthCheckRoute
from healthchecks.redis_healthcheck import HealthCheckRedis

from src.config import REDIS_URI
from src.lootboxes.equal.router import router as equal_lootbox_router
from src.lootboxes.weighted.router import router as weighted_lootbox_router

app = FastAPI(docs_url="/api")

app.include_router(equal_lootbox_router, prefix="/equal", tags=["equal lootboxes"])
app.include_router(weighted_lootbox_router, prefix="/weighted", tags=["weighted lootboxes"])

Instrumentator().instrument(app).expose(app)

_healthChecks = HealthCheckFactory()
_healthChecks.add(HealthCheckRedis(alias="redis", connection_uri=REDIS_URI, tags=["redis"]))
app.add_api_route('/health/redis', endpoint=healthCheckRoute(factory=_healthChecks))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
