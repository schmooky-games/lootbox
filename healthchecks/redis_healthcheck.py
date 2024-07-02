from fastapi_healthcheck.service import HealthCheckBase
from fastapi_healthcheck.enum import HealthCheckStatusEnum
from fastapi_healthcheck.domain import HealthCheckInterface
from typing import List
import redis


class HealthCheckRedis(HealthCheckBase, HealthCheckInterface):
    _connection_uri: str
    _tags: List[str]
    _message: str

    def __init__(self, connection_uri: str, alias: str, tags: List[str]) -> None:
        self._alias = alias
        self._connection_uri = connection_uri
        self._tags = tags

    def __checkHealth__(self) -> HealthCheckStatusEnum:
        res: HealthCheckStatusEnum = HealthCheckStatusEnum.UNHEALTHY
        try:
            connection = redis.from_url(self._connection_uri)
            if connection.ping():
                res = HealthCheckStatusEnum.HEALTHY
        except Exception as e:
            self._message = str(e)
        finally:
            if 'connection' in locals():
                connection.close()
        return res
