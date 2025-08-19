from typing import Annotated, Literal

from PIL import Image
from pydantic import Field

from backuper.actions.abstract import Action
from backuper.parameters import SubstitutedStr


class ImageReshapeAction(Action):
    type: Literal["reshape-image"]
    source: SubstitutedStr
    target: SubstitutedStr
    lossless: bool = True
    quality: Annotated[int, Field(ge=1, le=100)] = 80

    def run(self) -> None:
        image = Image.open(self.source)
        image.save(
            self.target,
            format="webp",
            lossless=self.lossless,
            quality=self.quality,
        )
