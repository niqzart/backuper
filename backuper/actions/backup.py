from collections.abc import Iterator
from os import system
from pathlib import Path
from typing import Literal

from backuper.actions.abstract import Action, BaseModelForbidExtra


class BackupExcludeSchema(BaseModelForbidExtra):
    directory_names: list[str] = []
    filename_patterns: list[str] = []


class BackupAction(Action):
    type: Literal["backup"]
    source: Path
    target: Path
    override_permissions: bool = False
    exclude: BackupExcludeSchema = BackupExcludeSchema()

    def collect_command(self) -> Iterator[str]:
        yield "robocopy"
        yield str(self.source)
        yield str(self.target)

        yield "/mir"

        if self.override_permissions:
            yield "/b"

        if self.exclude.directory_names:
            yield "/xd"
            yield from self.exclude.directory_names

        if self.exclude.filename_patterns:
            yield "/xf"
            yield from self.exclude.filename_patterns

    def run(self) -> None:
        system(" ".join(self.collect_command()))
