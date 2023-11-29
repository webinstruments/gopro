import datetime
from pathlib import Path
from typing import Optional
from loguru import logger
import requests
from config import search_response, token, storage_path

API_HEADERS = {
    "Authorization": token
}

MEDIA_FILES = search_response["_embedded"]["media"]


def download_file(url: str, store_path: Path, item_number: Optional[int]) -> None:
    dest_path = store_path
    if item_number and item_number > 1:
        file_name, file_ext = tuple(store_path.name.split("."))
        new_file_name = f"{file_name}_{item_number}.{file_ext}"
        dest_path = store_path.parent.joinpath(new_file_name)
        logger.info(f"File has multiple parts, renaming {store_path}")
    
    if dest_path.exists():
        logger.warning(f"Skipping {dest_path}.")
        return
    
    logger.info(f"Storing file {dest_path}...")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(dest_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    logger.info(f"Done storing file {dest_path}.")


def download(media_id: str, storage_path: Path) -> None:
    download_links = requests.get(f"https://api.gopro.com/media/{media_id}/download", headers=API_HEADERS).json()
    files = [u for u in download_links["_embedded"]["variations"] if u["label"] in ["source", "baked_source"]]
    logger.info(f"Got {len(files)} files.")
    assert len(files)
    for u in files:
        download_file(url=u["url"], store_path=storage_path, item_number=u.get("item_number"))
    

for m in MEDIA_FILES:
    file = m["filename"]
    id = m["id"]
    m_type = m["type"]
    item_count = m["item_count"]
    if not file and m_type == "MultiClipEdit":
        file = f"{id}.mp4"
    assert id
    assert file
    created_at_str = m["captured_at"]
    created_at = datetime.datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%SZ")
    
    folder_name = created_at.strftime("%d%m%Y")
    logger.info(f"Processing file {file}, date {folder_name}...")
    
    directory_path = Path(storage_path).joinpath(folder_name)
    directory_path.mkdir(exist_ok=True)
    file_path = directory_path.joinpath(file)

    if item_count == 1 and file_path.exists():
        logger.warning(f"File {file_path} already exists.")
        continue


    download(media_id=id, storage_path=file_path)
