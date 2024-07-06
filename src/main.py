from fastapi import FastAPI, Depends
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi_healthcheck import HealthCheckFactory, healthCheckRoute
from healthchecks.redis_healthcheck import HealthCheckRedis

from src.config import REDIS_URI
from src.lootboxes.router import router as general_router
from src.lootboxes.equal.router import router as equal_lootbox_router
from src.lootboxes.weighted.router import router as weighted_lootbox_router
from src.lootboxes.exclusive.router import router as exclusive_lootbox_router
from src.auth.router import router as auth_router, verify_token

app = FastAPI(docs_url="/api")

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(general_router, prefix="", tags=["general methods"], dependencies=[Depends(verify_token)])
app.include_router(equal_lootbox_router, prefix="/equal", tags=["equal lootboxes"]
                   , dependencies=[Depends(verify_token)])
app.include_router(weighted_lootbox_router, prefix="/weighted", tags=["weighted lootboxes"]
                   , dependencies=[Depends(verify_token)])
app.include_router(exclusive_lootbox_router, prefix="/exclusive", tags=["exclusive lootboxes"]
                   , dependencies=[Depends(verify_token)])

Instrumentator().instrument(app).expose(app)

_healthChecks = HealthCheckFactory()
_healthChecks.add(HealthCheckRedis(alias="redis", connection_uri=REDIS_URI, tags=["redis"]))
app.add_api_route('/health/redis', endpoint=healthCheckRoute(factory=_healthChecks))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
