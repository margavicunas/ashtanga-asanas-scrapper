from typing import TypedDict, List


class AsanaImageData(TypedDict):
    """Raw asana data as scraped from the website"""

    id: str
    name: str
    img_url: str
    downloaded_img_path: str


class ProcessedAsana(TypedDict):
    """Asana data with similar asanas ids"""

    id: str
    name: str
    img_url: str
    downloaded_img_path: str
    similar_asanas: List[str]
