from string import Template
from typing import Annotated

from pydantic import AfterValidator
from pydantic_core.core_schema import ValidationInfo


def substitute(incoming_string: str, info: ValidationInfo) -> str:
    if not isinstance(info.context, dict):
        raise RuntimeError

    template = Template(incoming_string)
    return template.substitute(info.context)


SubstitutedStr = Annotated[str, AfterValidator(substitute)]
