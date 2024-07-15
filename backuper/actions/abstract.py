from collections.abc import Iterator
from os import system

from backuper.utils import BaseModelForbidExtra


class Action(BaseModelForbidExtra):
    def run(self) -> None:
        raise NotImplementedError


class SubShellAction(Action):
    def collect_command(self) -> Iterator[str]:
        raise NotImplementedError

    def run(self) -> None:
        system(" ".join(self.collect_command()))
