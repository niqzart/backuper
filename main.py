from os import system

target_bases: list[str] = ["E:\\Backup\\"]  # , "F:\\Backup\\"]
source_paths: list[str] = ["D:\\Important", "D:\\Projects", "D:\\University"]
source_paths2: list[str] = [r"F:\Old", r"F:\Photos"]

def backup(source_paths: list[str], target_base: str, excluded: str = ""):
    if excluded != "":
        excluded = "/xd " + excluded

    for source_path in source_paths:
        if source_path.endswith("saves"):
            target_cont = source_path.rpartition("\\")[0].rpartition("\\")[2]
        else:
            target_cont = source_path.rpartition("\\")[2]
        target_path = target_base + target_cont
        system(f"robocopy {source_path} {target_path} /mir /b {excluded}")

    if target_base in target_bases:
        system(f"7za u {target_base[:-1]}.7z -uq0 {target_base}")


if __name__ == "__main__":
    input("Please move important but deleted files from Backup to Backlog and press Enter\n")
    
    with open("config.txt", encoding="utf-8") as f:
        excluded: str = " ".join([s for s in f.read().split("\n") if s != ""])

    for target_base in target_bases:
        backup(source_paths, target_base, excluded)
    # backup(source_paths2, "E:\\", excluded)
