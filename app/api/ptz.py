import logging

from fastapi import APIRouter
from pydantic import BaseModel, field_validator

router = APIRouter()
logger = logging.getLogger(__name__)

VALID_DIRECTIONS = {"up", "down", "left", "right", "home"}


class PTZCommand(BaseModel):
    direction: str

    @field_validator("direction")
    @classmethod
    def validate_direction(cls, v: str) -> str:
        if v not in VALID_DIRECTIONS:
            raise ValueError(f"direction must be one of {sorted(VALID_DIRECTIONS)}")
        return v


@router.post("/ptz")
async def ptz(cmd: PTZCommand):
    logger.info("PTZ command: %s", cmd.direction)
    return {"status": "ok"}
