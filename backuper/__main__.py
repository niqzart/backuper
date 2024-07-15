from collections import OrderedDict
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from pydantic import AfterValidator, Field, ValidationError
from pydantic_yaml import parse_yaml_file_as
from typer import Argument, FileText, Typer

from backuper.actions.backup import BackupAction
from backuper.utils import BaseModelForbidExtra
from backuper.variables import Variables

AnyAction = Annotated[BackupAction, Field(discriminator="type")]


def dotenv_loader(dotenv_filepath: Path) -> Path:
    load_dotenv(dotenv_filepath)
    return dotenv_filepath


class ConfigModel(BaseModelForbidExtra):
    dotenv: Annotated[Path, AfterValidator(dotenv_loader)]
    variables: Variables = {}
    actions: OrderedDict[str, AnyAction]

    def run(self) -> None:
        for action in self.actions.values():
            action.run()


cli = Typer()


@cli.command()
def main(config_file: Annotated[FileText, Argument(encoding="utf-8")]) -> None:
    # TODO defaults for filename
    try:
        config = parse_yaml_file_as(ConfigModel, config_file)
    except ValidationError as e:  # noqa: WPS329
        raise e  # TODO error handling for parsing

    config.run()


if __name__ == "__main__":
    cli()
