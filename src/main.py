from fastapi import FastAPI, Depends
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi_healthcheck import HealthCheckFactory, healthCheckRoute
from healthchecks.redis_healthcheck import HealthCheckRedis

from src.config import REDIS_URI
from src.error_handlers import setup_error_handlers
from src.lootboxes.router import router as general_router
from src.lootboxes.equal.router import router as equal_lootbox_router
from src.lootboxes.weighted.router import router as weighted_lootbox_router
from src.lootboxes.exclusive.router import router as exclusive_lootbox_router
from src.auth.router import router as auth_router, verify_token

tags_metadata = [
    {
        "name": "equal",
        "description": "Operations with equal lootboxes"
    },
    {
        "name": "weighted",
        "description": "Operations with weighted lootboxes"
    },
    {
        "name": "exclusive",
        "description": "Operations with exclusive lootboxes"
    }
]

app = FastAPI(docs_url="/api", openapi_tags=tags_metadata)

setup_error_handlers(app)

# app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(general_router, prefix="", tags=["general methods"])
app.include_router(equal_lootbox_router, prefix="/equal", tags=["equal"])
app.include_router(weighted_lootbox_router, prefix="/weighted", tags=["weighted"])
app.include_router(exclusive_lootbox_router, prefix="/exclusive", tags=["exclusive"])

Instrumentator().instrument(app).expose(app)

_healthChecks = HealthCheckFactory()
_healthChecks.add(HealthCheckRedis(alias="redis", connection_uri=REDIS_URI, tags=["redis"]))
app.add_api_route('/health/redis', endpoint=healthCheckRoute(factory=_healthChecks))
