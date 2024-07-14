from pydantic import BaseModel, ConfigDict


class BaseModelForbidExtra(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Action(BaseModelForbidExtra):
    def run(self) -> None:
        raise NotImplementedError
