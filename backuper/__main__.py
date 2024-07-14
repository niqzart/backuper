from typing import Annotated

from pydantic import BaseModel, ValidationError
from pydantic_yaml import parse_yaml_file_as
from typer import Argument, FileText, run


class ConfigModel(BaseModel):
    t: int


def main(config_file: Annotated[FileText, Argument(encoding="utf-8")]) -> None:
    # TODO defaults for filename
    try:
        config = parse_yaml_file_as(ConfigModel, config_file)
    except ValidationError as e:  # noqa: WPS329
        raise e  # TODO error handling for parsing

    print(config)  # noqa: T201 WPS421


if __name__ == "__main__":
    run(main)
