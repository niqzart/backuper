from os import getenv
from string import Template
from typing import Annotated

from dotenv import load_dotenv
from pydantic import AfterValidator
from pydantic_core.core_schema import ValidationInfo

from backuper.config import (
    AnyParameter,
    CLIArgumentParameterModel,
    ConfigModel,
    ConstantParameterModel,
    EnvironmentParameterModel,
)


def substitute(incoming_string: str, info: ValidationInfo) -> str:
    if not isinstance(info.context, dict):
        raise RuntimeError

    template = Template(incoming_string)
    return template.substitute(info.context)


SubstitutedStr = Annotated[str, AfterValidator(substitute)]


class ParameterLoader:
    def __init__(self, config: ConfigModel, cli_arguments: list[str]) -> None:
        self.config = config
        self.cli_arguments = cli_arguments

        if config.dotenv is not None:
            load_dotenv(config.dotenv)

    def load_parameter(self, name: str, parameter_data: AnyParameter) -> str:
        match parameter_data:
            case ConstantParameterModel():
                return parameter_data.value
            case EnvironmentParameterModel():
                value = getenv(name, default=parameter_data.default)
                if value is None:
                    raise EnvironmentError(
                        f"Environment variable '{name}' should be specified"
                    )
                return value
            case CLIArgumentParameterModel():
                if parameter_data.index >= len(self.cli_arguments):
                    raise EnvironmentError(
                        f"Argument '{name}' at position {parameter_data.index} should be specified"
                    )
                return self.cli_arguments[parameter_data.index]

    def load_all(self) -> dict[str, str]:
        return {
            name: self.load_parameter(name=name, parameter_data=parameter_data)
            for name, parameter_data in self.config.parameters.items()
        }
