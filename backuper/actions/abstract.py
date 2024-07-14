from pydantic import BaseModel, ConfigDict


class Action(BaseModel):
    model_config = ConfigDict(extra="forbid")
