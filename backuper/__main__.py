from typing import Annotated

from pydantic import ValidationError
from typer import Argument, FileText, Typer
from yaml import safe_load as safe_load_yaml

from backuper.config import ConfigModel
from backuper.parameters import ParameterLoader
from backuper.runner import ActionsModel, run_actions

cli = Typer(pretty_exceptions_enable=False)


@cli.command()
def main(
    config_file: Annotated[FileText, Argument(encoding="utf-8")],
    cli_arguments: Annotated[list[str] | None, Argument()] = None,
) -> None:
    # TODO defaults for filename

    loaded_config = safe_load_yaml(config_file)

    try:
        config = ConfigModel.model_validate(loaded_config)
    except ValidationError as e:  # noqa: WPS329 WPS440
        raise e  # TODO error handling for parsing

    parameter_loader = ParameterLoader(config=config, cli_arguments=cli_arguments or [])
    variables = parameter_loader.load_all()

    try:
        actions = ActionsModel.model_validate(config.actions, context=variables)
    except ValidationError as e:  # noqa: WPS329 WPS440
        raise e  # TODO error handling for parsing

    run_actions(actions=actions)


if __name__ == "__main__":
    cli()
