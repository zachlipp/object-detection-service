from typing import Optional

from pydantic import BaseModel, field_validator


class DetectionRequest(BaseModel):
    image_id: str


class ProcessRequest(BaseModel):
    image_id: str
    scaling_factor: Optional[float] = None

    @field_validator("scaling_factor")
    @classmethod
    def scaling_factor_bounded(cls, v):
        if v > 1 or v < 0.25:
            raise ValueError('"scaling_factor" must be between .25 and 1')
        return float(v)
