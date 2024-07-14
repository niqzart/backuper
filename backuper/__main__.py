from typing import Annotated

from typer import Argument, FileText, run


def main(config: Annotated[FileText, Argument(encoding="utf-8")]) -> None:
    # TODO defaults for filename
    print(type(config), config)  # noqa: T201 WPS421


if __name__ == "__main__":
    run(main)
