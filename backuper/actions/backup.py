from pathlib import Path
from typing import Literal

from backuper.actions.abstract import Action


class BackupAction(Action):
    type: Literal["backup"]
    source: Path
    target: Path
