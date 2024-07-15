from os import getenv
from string import Template
from typing import Annotated

from pydantic import AfterValidator


class VariableController:
    def __init__(self) -> None:
        self.variables: dict[str, str] = {}

    def load_variable(self, key: str, value: str | None) -> str:
        value = getenv(key, default=value)
        if value is None:
            raise EnvironmentError(f"Environment variable '{key}' should be specified")
        return value

    def load_variables(self, variables: dict[str, str | None]) -> dict[str, str]:
        self.variables = {
            key: self.load_variable(key=key, value=value)
            for key, value in variables.items()
        }
        return self.variables

    def substitute(self, incoming_string: str) -> str:
        template = Template(incoming_string)
        return template.substitute(self.variables)


vc = VariableController()

Variables = Annotated[dict[str, str | None], AfterValidator(vc.load_variables)]
SubstitutedStr = Annotated[str, AfterValidator(vc.substitute)]
