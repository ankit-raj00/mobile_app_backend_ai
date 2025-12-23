from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class Task(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    title: str
    raw_input: Optional[str] = None
    subject: Optional[str] = None
    topic: Optional[str] = None
    tags: List[str] = []
    type: str = Field(default="study") # study, code, revision
    status: str = Field(default="pending") # pending, in_progress, done
    priority: str = Field(default="medium") # low, medium, high
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "title": "Revise Volatility Modelling",
                "tags": ["GATE", "Econometrics"],
                "status": "pending",
                "priority": "high"
            }
        }
