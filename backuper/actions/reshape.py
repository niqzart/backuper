import re
from pathlib import Path
from typing import Annotated, Final, Literal

from PIL import Image, UnidentifiedImageError
from pydantic import Field

from backuper.actions.abstract import Action
from backuper.parameters import SubstitutedStr

RESHAPED_IMAGE_FORMAT: Final[str] = "webp"


class ImageReshapeAction(Action):
    type: Literal["reshape-images"]
    source: SubstitutedStr
    recursive: bool = False
    filename_regex: re.Pattern[str] | None = None
    replace_extension: bool = False
    delete_original: bool = False
    lossless: bool = True
    quality: Annotated[int, Field(ge=1, le=100)] = 80

    def is_filename_skipped(self, filename: str) -> bool:
        return (
            self.filename_regex is not None
            and self.filename_regex.fullmatch(filename) is None
        )

    def is_already_reshaped(self, image: Image.Image) -> bool:
        if image.format is None:
            return False
        return image.format.lower() == RESHAPED_IMAGE_FORMAT

    def generate_target_filename(self, source_filename: str) -> str:
        if self.replace_extension and "." in source_filename:
            source_filename = source_filename.rpartition(".")[0]
        return f"{source_filename}.{RESHAPED_IMAGE_FORMAT}"

    def reshape_image(self, path: Path) -> None:
        try:
            image = Image.open(path)
        except UnidentifiedImageError:
            return  # not an image

        with image:
            if self.is_already_reshaped(image=image):
                return

            target_filename = self.generate_target_filename(path.name)
            image.save(
                path.parent / target_filename,
                format=RESHAPED_IMAGE_FORMAT,
                lossless=self.lossless,
                quality=self.quality,
            )

        print(f"{path}: reshaped to {target_filename}")

        if self.delete_original:
            path.unlink()

    def reshape_images(self, source_path: Path) -> None:
        for path in sorted(source_path.iterdir(), key=lambda p: p.name):
            if self.is_filename_skipped(path.name):
                continue

            if self.recursive and path.is_dir():
                print(f"\n{source_path} reshaping images in directory")
                self.reshape_images(path)

            if not path.is_file():
                continue

            self.reshape_image(path)

    def run(self) -> None:
        source_path = Path(self.source)
        if source_path.is_file():
            self.reshape_image(source_path)
        elif source_path.is_dir():
            self.reshape_images(source_path)
        else:
            raise TypeError("Source is neither a file nor a directory")
