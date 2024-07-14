from collections import OrderedDict
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from pydantic_yaml import parse_yaml_file_as
from typer import Argument, FileText, run

from backuper.actions.backup import BackupAction

AnyAction = Annotated[BackupAction, Field(discriminator="type")]


class ConfigModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actions: OrderedDict[str, AnyAction]


def main(config_file: Annotated[FileText, Argument(encoding="utf-8")]) -> None:
    # TODO defaults for filename
    try:
        config = parse_yaml_file_as(ConfigModel, config_file)
    except ValidationError as e:  # noqa: WPS329
        raise e  # TODO error handling for parsing

    print(config)  # noqa: T201 WPS421


if __name__ == "__main__":
    run(main)
