from collections import OrderedDict
from typing import Annotated

from pydantic import Field, ValidationError
from pydantic_yaml import parse_yaml_file_as
from typer import Argument, FileText, run

from backuper.actions.backup import BackupAction
from backuper.utils import BaseModelForbidExtra
from backuper.variables import Variables

AnyAction = Annotated[BackupAction, Field(discriminator="type")]


class ConfigModel(BaseModelForbidExtra):
    variables: Variables = {}
    actions: OrderedDict[str, AnyAction]

    def run(self) -> None:
        for action in self.actions.values():
            action.run()


def main(config_file: Annotated[FileText, Argument(encoding="utf-8")]) -> None:
    # TODO defaults for filename
    try:
        config = parse_yaml_file_as(ConfigModel, config_file)
    except ValidationError as e:  # noqa: WPS329
        raise e  # TODO error handling for parsing

    config.run()


if __name__ == "__main__":
    run(main)
