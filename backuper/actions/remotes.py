from collections.abc import Iterator
from typing import Literal

from pydantic import AnyUrl, BaseModel

from backuper.actions.abstract import SubShellAction
from backuper.parameters import SubstitutedPath, SubstitutedStr


class SCPLocationData(BaseModel):
    username: SubstitutedStr | None = None
    password: SubstitutedStr | None = None
    host: SubstitutedStr | None = None
    path: SubstitutedPath

    def build_argument(self) -> str:
        if self.host is None:
            return self.path.as_posix()
        return AnyUrl.build(
            scheme="scp",
            username=self.username,
            password=self.password,
            host=self.host,
            path=self.path.as_posix(),
        ).unicode_string()


class SCPAction(SubShellAction):
    # TODO switch to rsync to delete the source directory

    type: Literal["scp"]
    source: SCPLocationData
    target: SCPLocationData
    preserve_timestamps: bool = True
    bandwidth_limit: int | None = None  # Kbit/s

    def collect_command(self) -> Iterator[str]:
        yield "scp"
        yield "-r"

        if self.preserve_timestamps:
            yield "-p"

        if self.bandwidth_limit is not None:
            yield "-l"
            yield str(self.bandwidth_limit)

        yield self.source.build_argument()

        yield self.target.build_argument()

    def is_failed(self, return_code: int) -> bool:
        return return_code != 0
