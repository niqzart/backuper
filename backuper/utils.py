import subprocess
from typing import Any

from pydantic import BaseModel, ConfigDict


class BaseModelForbidExtra(BaseModel):
    model_config = ConfigDict(extra="forbid")


def run_sub_shell(command: list[str]) -> subprocess.CompletedProcess[Any]:
    return subprocess.run(command, shell=True)  # noqa: S602 SCS103
