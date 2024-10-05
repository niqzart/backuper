import re
from collections.abc import Iterator
from pathlib import Path
from typing import Literal

from backuper.actions.abstract import Action, ActionError, SubShellAction
from backuper.utils import run_sub_shell
from backuper.variables import SubstitutedStr


class FromAndroidAction(Action):
    type: Literal["from-android"]
    source: SubstitutedStr
    filename_regex: re.Pattern[str] | None = None
    target: SubstitutedStr
    keep_timestamps_and_mode: bool = True

    def collect_ls_command(self) -> Iterator[str]:
        yield "adb"
        yield "shell"
        yield "ls"
        # `-l` could be used for a more detailed analysis
        yield str(self.source)

    def collect_pull_command(self, filename: str) -> Iterator[str]:
        yield "adb"
        yield "pull"
        yield "-p"

        if self.keep_timestamps_and_mode:
            yield "-a"

        yield f"{self.source}/{filename}"

        yield str(self.target.rstrip("/\\"))

    def is_filename_skipped(self, filename: str) -> bool:
        return (
            self.filename_regex is not None
            and self.filename_regex.fullmatch(filename) is None
        )

    def iter_filenames(self, stdout: str) -> Iterator[str]:
        for line in stdout.split("\r\n"):
            if line == "":
                continue
            if self.is_filename_skipped(line):
                print(f"Skipping file: {line}")
                continue
            # mb more conditions based on `-l` (e.g. exclude directories)
            yield line

    def run(self) -> None:
        Path(self.target).mkdir(parents=True, exist_ok=True)

        ls_result = run_sub_shell(list(self.collect_ls_command()), capture_output=True)
        if ls_result.returncode != 0:
            raise ActionError(ls_result.returncode, step_name="listing")

        for filename in self.iter_filenames(ls_result.stdout.decode("utf-8")):
            pull_result = run_sub_shell(list(self.collect_pull_command(filename)))
            if pull_result.returncode != 0:
                raise ActionError(pull_result.returncode, step_name="copying")


class ToAndroidAction(SubShellAction):
    type: Literal["to-android"]
    source: SubstitutedStr
    target: SubstitutedStr
    keep_timestamps_and_mode: bool = True

    def collect_command(self) -> Iterator[str]:
        yield "adb"
        yield "push"
        yield "-p"

        if self.keep_timestamps_and_mode:
            yield "-a"

        yield str(self.source)
        yield str(self.target)

    def is_failed(self, return_code: int) -> bool:
        return return_code != 0
