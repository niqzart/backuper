from backuper.utils import BaseModelForbidExtra


class Action(BaseModelForbidExtra):
    def run(self) -> None:
        raise NotImplementedError
