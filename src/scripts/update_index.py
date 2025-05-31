import sys
from pathlib import Path

from src.media_indexing.folder_index import (
    apply_new_media_paths,
    get_folders,
    get_updated_media_paths,
    reindex_folders,
)


def main(input_dir: Path) -> None:
    print(input_dir)
    mapping = get_updated_media_paths(input_dir)
    apply_new_media_paths(mapping)
    folders = get_folders(input_dir)
    reindex_folders(folders)


if __name__ == "__main__":
    main(input_dir=Path(sys.argv[1]))
