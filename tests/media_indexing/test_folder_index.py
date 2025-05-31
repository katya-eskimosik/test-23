import os
import shutil
from pathlib import Path
import pytest

from src.media_indexing.folder_index import (
    Media,
    Folder,
    get_artist,
    remove_artist,
    remove_counter,
    get_folders,
    get_folder_files,
    get_updated_media_paths,
    apply_new_media_paths,
    reindex_folders,
)
from src.const import VARIOUS_ARTISTS_NAME


@pytest.fixture
def temp_dir(tmp_path): #Тестовая директория
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

#Обработка названий файла

def test_get_artist(): #возврат артиста
    assert get_artist("song [Artist A].mp3") == "Artist A"
    assert get_artist("track.mp3") is None
    with pytest.raises(ValueError):
        get_artist("song [Artist A] [Artist B].mp3")


def test_remove_artist(): #удаление артиста
   # assert remove_artist("song [Artist A].mp3") == "song.mp3"
    assert remove_artist("track.mp3") == "track.mp3"


def test_remove_counter(): #удаление счетчика
    assert remove_counter("Artist A (5)") == "Artist A"
    assert remove_counter("VA (10)") == "VA"


def test_media_rename(): #разделение названия на части
    media = Media(Path("song [Artist A].mp3"))
    assert media.title == "song"
    assert media.artist_name == "Artist A"



def test_folder_title(temp_dir): #названия папок в новой структуре
    
    test_folder = temp_dir / "Artist A (5)"
    test_folder.mkdir()
    
    folder = Folder(test_folder)
    assert folder.title == "Artist A"
    

    
    test_folder = temp_dir / "VA (10)"
    test_folder.mkdir()
    
    folder = Folder(test_folder)
    assert folder.title == "VA"


def test_folder_counter(temp_dir): #счетчик файлов

    test_folder = temp_dir / "Test Folder"
    test_folder.mkdir()
    (test_folder / "song1.mp3").touch()
    (test_folder / "song2.mp3").touch()
    (test_folder / "song3.mp3").touch()
    
    folder = Folder(test_folder)
    assert folder.get_counter() == 3
    
    (test_folder / "song4.mp3").touch() #добавление
    assert folder.get_counter() == 4

    (test_folder / "song1.mp3").unlink() #удаление
    assert folder.get_counter() == 3


def test_media_class(temp_dir): #Media

    media_path = temp_dir / "Chill Vibes" / "track1 [Artist A].mp3"
    media = Media(media_path)
    assert media.artist_name == "Artist A"
    assert media.title == "track1"
    

    media.rename_update() #переименование файла
    assert media.path.name == "track1 [Artist A].mp3"


def test_folder_class(temp_dir): #Folder
    folder_path = temp_dir / "Chill Vibes"
    folder = Folder(folder_path)
    assert folder.title == "Chill Vibes" #название
    assert folder.get_counter() == 3 #счетчик
    
    folder.rename_with_counter() 
    assert folder.path.name == "Chill Vibes (3)" #новое название папки


def test_get_folders(temp_dir):
    folders = get_folders(temp_dir)
    assert len(folders) == 4 #количества папок
    folder_names = {f.title for f in folders}
    assert folder_names == {"Chill Vibes", "Classic Hits", "Jazz Essentials", "Rock Anthems"}  #имена папок


def test_get_folder_files(temp_dir): 
    folder_path = temp_dir / "Chill Vibes"
    files = get_folder_files(folder_path)
    assert len(files) == 3 #количество файлов
    file_names = {f.name for f in files}
    assert file_names == {"song2 [Artist B].mp3", "track1 [Artist A].mp3", "track3.mp3"} #название файлов


def test_get_updated_media_paths(temp_dir):
    mapping = get_updated_media_paths(temp_dir)
    
    total_files = sum(len(get_folder_files(d)) for d in temp_dir.iterdir() if d.is_dir())
    assert len(mapping) == total_files #количество файлов
#названия новый папок
    for old_path, new_path in mapping.items():
        if "[Artist A]" in old_path.name:
            assert new_path.parent.name == "Artist A"
        elif "[Artist B]" in old_path.name: 
            assert new_path.parent.name == "Artist B"
        elif "[Artist C]" in old_path.name: 
            assert new_path.parent.name == "Artist C"
        elif "[Artist D]" in old_path.name: 
            assert new_path.parent.name == "Artist D"
        else:
            assert new_path.parent.name == VARIOUS_ARTISTS_NAME


def test_apply_new_media_paths(temp_dir):
    mapping = get_updated_media_paths(temp_dir)
    apply_new_media_paths(mapping)
    
    artist_folders = {d.name for d in temp_dir.iterdir() if d.is_dir()}
    expected_folders = {"Artist A", "Artist B", "Artist C", "Artist D", VARIOUS_ARTISTS_NAME}
    assert artist_folders == expected_folders

    #количество файлов в папках
    assert len(list((temp_dir / "Artist A").iterdir())) == 2
    assert len(list((temp_dir / "Artist B").iterdir())) == 2
    assert len(list((temp_dir / "Artist C").iterdir())) == 1
    assert len(list((temp_dir / "Artist D").iterdir())) == 1
    assert len(list((temp_dir / VARIOUS_ARTISTS_NAME).iterdir())) == 4


def test_reindex_folders(temp_dir): 
    # Get list of folders
    folders = get_folders(temp_dir)
    reindex_folders(folders)
    
    for folder in temp_dir.iterdir():
        if folder.is_dir():
            assert "(" in folder.name and ")" in folder.name #есть счетчик


#def test_empty_artist_folder(temp_dir): #пустая папка артиста
 #   (temp_dir / "Empty Artist").mkdir()
  #  
#
 #   mapping = get_updated_media_paths(temp_dir)
           
  #  apply_new_media_paths(mapping)
    
   # assert not (temp_dir / "Empty Artist").exists() # Проверка, что пустая папка артиста не создана в новой структуре
    
    #assert (temp_dir / "Artist A").exists() 
    #assert (temp_dir / "Artist B").exists() 
    #assert (temp_dir / "VA").exists() 
