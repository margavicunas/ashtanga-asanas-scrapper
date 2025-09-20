import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PIL import Image
from io import BytesIO
import logging
from typing import TypedDict


class AsanaImageData(TypedDict):
    id: str
    name: str
    img_url: str

class DownloadedAsanaImageData(TypedDict):
    id: str
    name: str
    path: str


class AshtangaAsanasScraper:
    def __init__(self, url: str, folder_hint_name: str, output_dir: str = "asanas"):
        self.url = url
        self.output_dir = output_dir
        self.folder_hint_name = folder_hint_name
        self.session = requests.Session()
        self.downloaded_asana_images_data: list[DownloadedAsanaImageData] = []

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def get_page_content(self) -> str | None:
        """Fetch the webpage content"""
        try:
            response = self.session.get(self.url)
            response.raise_for_status()
            return str(response.text)
        except requests.RequestException as e:
            logging.error(f"Error fetching page: {e}")
            return None

    def create_asana_id(self, name: str) -> str:
        """Create a URL-friendly ID from asana name"""
        return "".join(
            c.lower() for c in name if c.isalnum() or c in ("-", "_")
        ).strip()

    def get_asana_name(self, asana_img: dict) -> str | None:
        if asana_img.get("title"):
            return asana_img.get("title")
        if asana_img.get("alt"):
            return asana_img.get("alt")
        if asana_img.get("src"):
            return str(asana_img.get("src")).split("/")[-1].split(".")[0]
        logging.error(f"No asana name found for {asana_img}, returning None")
        return None

    def extract_asanas_images_data(self, html_content: str) -> list[AsanaImageData]:
        """Extract asana names and image URLs from the page"""
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, "html.parser")
        asanas_images_data: list[AsanaImageData] = []

        for asana_img in soup.find_all(["img"]):
            asana_img_src = asana_img.get("src")
            if not asana_img_src:
                logging.info(
                    f"Skipping {asana_img_src} because it doesn't contain an image. Who knows what this is."
                )
                continue

            if self.folder_hint_name not in asana_img_src:
                logging.info(
                    f"Skipping {asana_img_src} because it doesn't contain {self.folder_hint_name}. Probably not an asana image."
                )
                continue

            asana_name = self.get_asana_name(asana_img)
            if not asana_name:
                logging.error(f"No asana name found for {asana_img}, skipping")
                continue

            asana_id = self.create_asana_id(asana_name)
            img_url = urljoin(self.url, asana_img_src)
            asanas_images_data.append(AsanaImageData(id=asana_id, name=asana_name, img_url=img_url))

        return asanas_images_data

    def download_image(self, image_url: str, asana_id: str) -> str | None:
        """Download and save an image given an image URL and an asana ID"""
        try:
            response = self.session.get(image_url)
            response.raise_for_status()

            filename = f"{asana_id}.png"
            filepath = os.path.join(self.output_dir, filename)

            img = Image.open(BytesIO(response.content))

            if img.mode in ("RGBA", "LA"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "RGBA":
                    background.paste(img, mask=img.split()[3])
                else:
                    background.paste(img, mask=img.split()[1])
                img = background

            img.save(filepath, "PNG")
            logging.info(f"Successfully saved {filename}")
            return filepath
        except Exception as e:
            logging.error(f"Error downloading image for {asana_id}: {e}")
            return None

    def export_data_to_json(self) -> None:
        """Export asana data to JSON file"""
        json_path = os.path.join(self.output_dir, "asanas.json")
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(self.downloaded_asana_images_data, f, indent=2, ensure_ascii=False)
            logging.info(f"Successfully exported data to {json_path}")
        except Exception as e:
            logging.error(f"Error exporting JSON data: {e}")

    def scrape_and_export_asanas(self) -> None:
        """Main scraping method and JSON export"""
        logging.info("Starting scraping process...")

        html_content = self.get_page_content()
        if not html_content:
            logging.error("Failed to get page content")
            return

        asanas_images_data = self.extract_asanas_images_data(html_content)
        logging.info(
            f"Found {len(asanas_images_data)} asanas, will proceed to download and save them."
        )

        for asana in asanas_images_data:
            path = self.download_image(asana["img_url"], asana["id"])
            if not path:
                logging.error(f"Failed to download image for {asana['id']}, skipping")
                continue

            self.downloaded_asana_images_data.append(DownloadedAsanaImageData(id=asana["id"], name=asana["name"], path=path))

        self.export_data_to_json()

        logging.info("Scraping completed")
