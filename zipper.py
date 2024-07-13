from os import listdir, system
from pathlib import Path

path = Path(r"F:\temp")

for folder in listdir(path):
    target = path / folder
    if target.is_file():
        continue
    print(target)
    if system(f'7za u "{target}.7z" -uq0 "{target}"'):
        break
