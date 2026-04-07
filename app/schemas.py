from pydantic import BaseModel

class LookalikeResponse(BaseModel):
    success: bool
    message: str
    match_name: str | None = None
    similarity: float | None = None
    image_url: str | None = None
