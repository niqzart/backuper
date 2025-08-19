from enum import StrEnum
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import Field

from backuper.utils import BaseModelForbidExtra


class ParameterSource(StrEnum):
    CONSTANT = "constant"
    ENVIRONMENT = "environment"
    CLI_ARGUMENT = "cli-argument"


class ConstantParameterModel(BaseModelForbidExtra):
    source: Literal[ParameterSource.CONSTANT] = ParameterSource.CONSTANT
    value: str


class EnvironmentParameterModel(BaseModelForbidExtra):
    source: Literal[ParameterSource.ENVIRONMENT] = ParameterSource.ENVIRONMENT
    default: str | None = None


class CLIArgumentParameterModel(BaseModelForbidExtra):
    source: Literal[ParameterSource.CLI_ARGUMENT] = ParameterSource.CLI_ARGUMENT
    index: int = 0


AnyParameter = Annotated[
    ConstantParameterModel | EnvironmentParameterModel | CLIArgumentParameterModel,
    Field(discriminator="source"),
]


class ConfigModel(BaseModelForbidExtra):
    dotenv: Path | None = None
    parameters: dict[str, AnyParameter] = {}
    actions: Any
