from collections import OrderedDict
from os import getenv
from pathlib import Path
from typing import Annotated, Any

from dotenv import load_dotenv
from pydantic import Field, RootModel, ValidationError
from typer import Argument, FileText, Typer
from yaml import safe_load as safe_load_yaml

from backuper.actions.abstract import ActionError
from backuper.actions.backup import BackupAction
from backuper.actions.compress import CompressAction
from backuper.utils import BaseModelForbidExtra


class ConfigModel(BaseModelForbidExtra):
    dotenv: Path | None = None
    variables: dict[str, str | None] = {}
    actions: Any


def load_variable(name: str, default_value: str | None) -> str:
    value = getenv(name, default=default_value)
    if value is None:
        raise EnvironmentError(f"Environment variable '{name}' should be specified")
    return value


def load_variables(config: ConfigModel) -> dict[str, str]:
    if config.dotenv is not None:
        load_dotenv(config.dotenv)

    return {
        name: load_variable(name=name, default_value=default_value)
        for name, default_value in config.variables.items()
    }


AnyAction = Annotated[BackupAction | CompressAction, Field(discriminator="type")]
ActionsModel = RootModel[OrderedDict[str, AnyAction]]


cli = Typer()


@cli.command()
def main(config_file: Annotated[FileText, Argument(encoding="utf-8")]) -> None:
    # TODO defaults for filename

    loaded_config = safe_load_yaml(config_file)

    try:
        config = ConfigModel.model_validate(loaded_config)
    except ValidationError as e:  # noqa: WPS329 WPS440
        raise e  # TODO error handling for parsing

    variables = load_variables(config)

    try:
        actions = ActionsModel.model_validate(config.actions, context=variables)
    except ValidationError as e:  # noqa: WPS329 WPS440
        raise e  # TODO error handling for parsing

    for action_name, action in actions.root.items():
        try:
            action.run()
        except ActionError as e:  # noqa: WPS440
            raise RuntimeError(
                f"Action '{action_name}' failed with code {e.return_code}"
            )


if __name__ == "__main__":
    cli()
