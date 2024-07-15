from collections import OrderedDict
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from pydantic import AfterValidator, Field, ValidationError
from pydantic_yaml import parse_yaml_file_as
from typer import Argument, FileText, Typer

from backuper.actions.abstract import ActionError
from backuper.actions.backup import BackupAction
from backuper.actions.compress import CompressAction
from backuper.utils import BaseModelForbidExtra
from backuper.variables import Variables

AnyAction = Annotated[BackupAction | CompressAction, Field(discriminator="type")]


def dotenv_loader(dotenv_filepath: Path) -> Path:
    load_dotenv(dotenv_filepath)
    return dotenv_filepath


class ConfigModel(BaseModelForbidExtra):
    dotenv: Annotated[Path, AfterValidator(dotenv_loader)]
    variables: Variables = {}
    actions: OrderedDict[str, AnyAction]

    def run(self) -> None:
        for action_name, action in self.actions.items():
            try:
                action.run()
            except ActionError as e:
                raise RuntimeError(
                    f"Action '{action_name}' failed with code {e.return_code}"
                )


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
