from pydantic import BaseModel, ConfigDict


class Action(BaseModel):
    model_config = ConfigDict(extra="forbid")

    def run(self) -> None:
        raise NotImplementedError
