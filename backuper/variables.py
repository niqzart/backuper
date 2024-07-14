from string import Template
from typing import Annotated

from pydantic import AfterValidator


class VariableController:
    def __init__(self) -> None:
        self.variables: dict[str, str] | None = None

    def load_variables(self, variables: dict[str, str]) -> dict[str, str]:
        self.variables = variables
        return variables

    def substitute(self, incoming_string: str) -> str:
        template = Template(incoming_string)
        return template.substitute(self.variables or {})


vc = VariableController()

Variables = Annotated[dict[str, str], AfterValidator(vc.load_variables)]
SubstitutedStr = Annotated[str, AfterValidator(vc.substitute)]
