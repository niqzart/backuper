import shutil
from collections.abc import Iterator
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field

from backuper.actions.abstract import SubShellAction
from backuper.variables import SubstitutedStr


class SplitAction(SubShellAction):
    type: Literal["split"]
    source: SubstitutedStr
    target: SubstitutedStr
    archive_name: SubstitutedStr
    volume_size: Annotated[SubstitutedStr, Field(pattern=r"\d+[bkmg]")]

    def collect_command(self) -> Iterator[str]:
        yield "7za"
        yield "a"
        yield str(Path(self.target) / f"{self.archive_name}.7z")

        if self.volume_size:
            yield f"-v{self.volume_size}"

        yield self.source

    def run(self) -> None:
        if Path(self.target).is_dir():
            shutil.rmtree(Path(self.target))
        Path(self.target).mkdir(exist_ok=True)
        super().run()

    def is_failed(self, return_code: int) -> bool:
        return return_code != 0