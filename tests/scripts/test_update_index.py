import shutil
from pathlib import Path
import pytest

from src.media_indexing.folder_index import (
    Media,
    Folder,
    get_artist,
    remove_artist,
    get_folders,
    get_folder_files,
    get_updated_media_paths,
    apply_new_media_paths,
    reindex_folders,
)
from src.const import VARIOUS_ARTISTS_NAME
from src.scripts.update_index import main as update_index


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory with test files."""
    # Create test directory structure
    test_dirs = {
        "Chill Vibes": [
            "song2 [Artist B].mp3",
            "track1 [Artist A].mp3",
            "track3.mp3",
        ],
        "Classic Hits": [
            "song1 [Artist B].mp3",
            "song3.mp3",
            "track2 [Artist A].mp3",
        ],
        "Jazz Essentials": [
            "jazz_track1.flac",
            "jazz_track2 [Artist C].mp3",
        ],
        "Rock Anthems": [
            "rock_song1.mp3",
            "rock_song2 [Artist D].flac",
        ],
    }

    for dir_name, files in test_dirs.items():
        dir_path = tmp_path / dir_name
        dir_path.mkdir()
        for file_name in files:
            (dir_path / file_name).touch()

    return tmp_path


def test_update_index_integration(temp_dir):

    update_index(temp_dir)
    

    artist_folders = {d.name for d in temp_dir.iterdir() if d.is_dir()}
    expected_folders = {"Artist A (2)", "Artist B (2)", "Artist C (1)", "Artist D (1)", "VA (4)"}
    assert artist_folders == expected_folders #структура новая
    
    #наполнение папок артистов
    artist_a_files = {f.name for f in (temp_dir / "Artist A (2)").iterdir()}
    assert artist_a_files == {"track1 [Artist A].mp3", "track2 [Artist A].mp3"}
    
    artist_b_files = {f.name for f in (temp_dir / "Artist B (2)").iterdir()}
    assert artist_b_files == {"song1 [Artist B].mp3", "song2 [Artist B].mp3"}
    
    artist_c_files = {f.name for f in (temp_dir / "Artist C (1)").iterdir()}
    assert artist_c_files == {"jazz_track2 [Artist C].mp3"}
    
    artist_d_files = {f.name for f in (temp_dir / "Artist D (1)").iterdir()}
    assert artist_d_files == {"rock_song2 [Artist D].flac"}
    
    va_files = {f.name for f in (temp_dir / "VA (4)").iterdir()}
    assert va_files == {"jazz_track1.flac", "rock_song1.mp3", "track3.mp3", "song3.mp3"}


def test_update_index_empty_dir(tmp_path): #пустая папка
    update_index(tmp_path)
    assert len(list(tmp_path.iterdir())) == 0


def test_update_index_single_file(temp_dir): #один файл
    test_dir = temp_dir / "Test Dir"
    test_dir.mkdir()
    (test_dir / "single [Artist X].mp3").touch()
    
    update_index(temp_dir)
    

    assert (temp_dir / "Artist X (1)").exists()
    assert (temp_dir / "Artist X (1)" / "single [Artist X].mp3").exists()
    assert not test_dir.exists() 