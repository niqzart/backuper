import re
from collections.abc import Iterator
from typing import Literal

from pydantic import AnyUrl, BaseModel

from backuper.actions.abstract import SubShellAction
from backuper.parameters import SubstitutedPath, SubstitutedStr


class SCPLocationData(BaseModel):
    username: SubstitutedStr | None = None
    password: SubstitutedStr | None = None
    host: SubstitutedStr | None = None
    port: int | None = None
    path: SubstitutedPath

    def build_argument(self) -> str:
        if self.host is None:
            return self.path.as_posix()
        return AnyUrl.build(
            scheme="scp",
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            path=self.path.as_posix(),
        ).unicode_string()


class SCPAction(SubShellAction):
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


class SSHAction(SubShellAction):
    # TODO maybe convert to a python-based solution

    type: Literal["ssh"]

    username: SubstitutedStr | None = None
    password: SubstitutedStr | None = None
    host: SubstitutedStr
    port: int | None = None

    command: SubstitutedStr

    expected_exit_codes: set[int] = {0}

    def collect_command(self) -> Iterator[str]:
        yield "ssh"

        yield AnyUrl.build(
            scheme="ssh",
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
        ).unicode_string()

        yield self.command

    def is_failed(self, return_code: int) -> bool:
        return return_code not in self.expected_exit_codes


class RSyncLocationData(BaseModel):
    username: SubstitutedStr | None = None
    password: SubstitutedStr | None = None
    host: SubstitutedStr | None = None
    path: SubstitutedPath

    @property
    def path_for_rsync(self) -> str:
        return re.sub("^([A-Z]):/", r"/cygdrive/\1/", self.path.as_posix(), count=1)

    def build_argument(self) -> str:
        if self.host is None:
            return self.path_for_rsync
        remote_location = (
            AnyUrl.build(
                scheme="rsync",
                username=self.username,
                password=self.password,
                host=self.host,
            )
            .unicode_string()
            .removeprefix("rsync://")
        )
        return f"{remote_location}:{self.path_for_rsync}"


class RSyncBackupAction(SubShellAction):
    type: Literal["rsync-backup"]

    source: RSyncLocationData
    target: RSyncLocationData

    preserve_timestamps: bool = True
    use_transport_compression: bool = True
    override_partial_files: bool = False
    bandwidth_limit: int | None = None  # KB/s
    remote_shell: SubstitutedPath | None = None

    # TODO: exclude / include

    def collect_command(self) -> Iterator[str]:
        yield "rsync"
        yield "--recursive"
        yield "--delete"
        yield "--progress"

        if self.preserve_timestamps:
            yield "--times"

        if self.use_transport_compression:
            yield "--compress"

        if not self.override_partial_files:
            yield "--partial"

        if self.bandwidth_limit is not None:
            yield "--bwlimit"
            yield str(self.bandwidth_limit)

        if self.remote_shell is not None:
            yield "--rsh"
            yield self.remote_shell.as_posix()

        yield self.source.build_argument()

        yield self.target.build_argument()

    def is_failed(self, return_code: int) -> bool:
        return return_code != 0
