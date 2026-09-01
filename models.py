from pydantic import BaseModel, Field
from enum import Enum

class Environment(str, Enum):
    prod = "prod"
    test4 = "test4"
    stage = "stage"

class DeploymentStatus(str, Enum):
    healthy = "healthy"
    degraded = "degraded"


class Deployment(BaseModel):
    service: str = Field(min_length=1)
    environment: Environment
    version: str = Field(min_length=1)
    status: DeploymentStatus