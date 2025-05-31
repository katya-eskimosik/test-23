import re
import shutil
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path

from src.const import VARIOUS_ARTISTS_NAME

ARTIST_PTRN = re.compile(r"\[(.+?)\]")


def get_artist(s: str) -> str | None:
    res: list[str] = ARTIST_PTRN.findall(s)
    if len(res) > 1:
        raise ValueError(f"Got more than one artist in a string: {s}")
    if not res:
        return None
    return res[0].title()


def remove_artist(s: str) -> str:
    return ARTIST_PTRN.sub("", s).strip()


class Media:
    def __init__(self, path: Path) -> None:
        if path.is_dir():
            raise ValueError(f"{path} is a dir, but its expected to be")

        self.path = path
        self.artist_name: str | None = get_artist(self.path.stem)
        self.title = remove_artist(self.path.stem)

    def rename_update(self) -> None:
        new_name = self.title
        if self.artist_name is not None:
            new_name += f" [{self.artist_name}]"
        new_path = self.path.with_name(f"{new_name}{self.path.suffix}")
        self.path = self.path.rename(new_path)


def remove_counter(s: str) -> str:
    COUNTER_PTRN = re.compile(r"\((\d+)\)$")
    return COUNTER_PTRN.sub("", s).strip()


class Folder:
    def __init__(self, path: Path) -> None:
        if not path.is_dir():
            raise ValueError(f"{path} is not a dir, but its expected to be")

        self.path = path
        self.title = remove_counter(self.path.name)

    def get_media_list(self) -> list[Media]:
        media_paths = get_folder_files(self.path)
        return [Media(p) for p in media_paths]

    def get_counter(self) -> int:
        return len(self.get_media_list())

    def get_new_folder_name(self) -> str:
        return f"{self.title} ({self.get_counter()})".strip()

    def rename_with_counter(self) -> None:
        new_name = self.get_new_folder_name()
        new_path = self.path.with_name(new_name)
        shutil.move(self.path, new_path)
        self.path = new_path


def get_folders(path: Path) -> list[Folder]:
    folders = [p for p in path.iterdir() if p.is_dir() and not p.name.startswith(".")]
    return [Folder(path) for path in folders]


def get_folder_files(path: Path) -> list[Path]:
    return [p for p in path.iterdir() if not p.name.startswith(".")]


def get_updated_media_paths(base_dir: Path) -> dict[Path, Path]:
    media_mapping: dict[Path, Path] = {}
    folders = get_folders(base_dir)
    artist_to_media: dict[str, list[Media]] = defaultdict(list)

    for folder in folders:
        for media in folder.get_media_list():
            artist = media.artist_name
            if artist is None:
                artist = VARIOUS_ARTISTS_NAME

            artist_to_media[artist].append(media)

    for artist, medias in artist_to_media.items():
        folder_path = base_dir / artist
        for media in medias:
            new_path = folder_path / media.path.name
            media_mapping[media.path] = new_path

    return media_mapping


def apply_new_media_paths(mapping: dict[Path, Path]) -> None:
    old_folders = [p.parent for p in mapping]

    for old_path, new_path in mapping.items():
        new_path.parent.mkdir(exist_ok=True)
        old_path.rename(new_path)

    for folder in set(old_folders):
        if len(get_folder_files(folder)) == 0:
            if any(p.is_dir() for p in folder.iterdir()):
                raise ValueError(f"Found directory in one of the folders that's not supposed to have it: {folder}")
            shutil.rmtree(folder)


def reindex_folders(folders: Iterable[Folder]) -> None:
    for folder in folders:
        for media in folder.get_media_list():
            media.rename_update()
        folder.rename_with_counter()
