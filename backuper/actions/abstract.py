import subprocess
from collections.abc import Iterator

from backuper.utils import BaseModelForbidExtra


class Action(BaseModelForbidExtra):
    def run(self) -> None:
        raise NotImplementedError


class SubShellAction(Action):
    def collect_command(self) -> Iterator[str]:
        raise NotImplementedError

    def run(self) -> None:
        subprocess.run(list(self.collect_command()))  # noqa: S603
