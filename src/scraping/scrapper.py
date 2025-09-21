import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PIL import Image
from io import BytesIO
import logging
from src.types.asana_types import AsanaImageData
from concurrent.futures import ThreadPoolExecutor, as_completed

DEFAULT_MAX_WORKERS = 4
DEVVYOGA_URL = "https://www.devvratyoga.com/learning-resources/ashtanga-yoga-asanas-with-names-images/"
DEVVYOGA_FOLDER_HINT_NAMES = ["uploads/2019/07/", "uploads/2019/08/"]


class AshtangaAsanasScraper:
    def __init__(
        self,
        url: str,
        folder_hint_names: list[str],
        output_dir: str = "data/asanas",
        max_workers: int = DEFAULT_MAX_WORKERS,
    ):
        """
        Initialize the scraper with the target URL and configuration.

        Args:
            url: The URL of the page to scrape. Defaults to DEVVYOGA_URL.
            folder_hint_name: The hint name of the folder where the asanas images are located. Defaults to DEVVYOGA_FOLDER_HINT_NAMES.
            output_dir: The directory to save the asanas json file and the images folder.
            max_workers: The maximum number of workers to use for parallel processing.
        """
        self.url = url
        self.folder_hint_names = folder_hint_names
        self.output_dir = output_dir
        self.images_output_dir = os.path.join(self.output_dir, "images")
        self.session = requests.Session()
        self.asanas_images_data: list[AsanaImageData] = []
        self.max_workers = max_workers

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if not os.path.exists(self.images_output_dir):
            os.makedirs(self.images_output_dir)

        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def scrape_and_export_asanas(self) -> None:
        """
        Main public method to start the scraping process and export results.
        This is the main entry point for using the scraper.
        """
        logging.info("Starting scraping process...")

        html_content = self._get_page_content()
        if not html_content:
            logging.error("Failed to get page content")
            return

        self.asanas_images_data = self._extract_asanas_images_data(html_content)
        self._export_data_to_json()

        logging.info("Scraping completed")

    def _get_page_content(self) -> str | None:
        """
        Fetches the webpage content.

        Returns:
            The webpage content as a string.
        """
        try:
            response = self.session.get(self.url)
            response.raise_for_status()
            return str(response.text)
        except requests.RequestException as e:
            logging.error(f"Error fetching page: {e}")
            return None

    def _create_asana_id(self, name: str) -> str:
        """Creates a URL-friendly ID from asana name.

        Args:
            name: The name of the asana.

        Returns:
            The URL-friendly ID as a string.
        """
        name = "-".join(word for word in name.split() if word)
        return "".join(
            c.lower() for c in name if c.isalnum() or c in ("-", "_")
        ).strip()

    def _get_asana_name(self, asana_img: dict) -> str | None:
        """
        Extracts asana name from image metadata.

        Args:
            asana_img: The image metadata.

        Returns:
            The asana name as a string or None if no name is found.
        """
        if asana_img.get("title"):
            return asana_img.get("title")
        if asana_img.get("alt"):
            return asana_img.get("alt")
        if asana_img.get("src"):
            return str(asana_img.get("src")).split("/")[-1].split(".")[0]
        logging.error(f"No asana name found for {asana_img}, returning None")
        return None

    def _extract_single_asana_image_data(
        self, asana_img: dict
    ) -> AsanaImageData | None:
        """
        Processes a single asana image. It checks the image metadata for the asana name and creates an ID
        from the name as well as downloading the image.

        Args:
            asana_img: The image metadata.

        Returns:
            The asana image data as an AsanaImageData object or None.
        """
        try:
            asana_img_src = asana_img.get("src")
            if not asana_img_src:
                logging.info(
                    f"Skipping {asana_img_src} because it doesn't contain an image. Who knows what this is."
                )
                return None

            if not any(
                folder_hint_name in asana_img_src
                for folder_hint_name in self.folder_hint_names
            ):
                logging.info(
                    f"Skipping {asana_img_src} because it doesn't contain any of the folder hint names {self.folder_hint_names}. Probably not an asana image."
                )
                return None

            asana_name = self._get_asana_name(asana_img)
            if not asana_name:
                logging.error(f"No asana name found for {asana_img}, skipping")
                return None

            asana_id = self._create_asana_id(asana_name)
            img_url = urljoin(self.url, asana_img_src)
            downloaded_img_path = self._download_image(img_url, asana_id)
            if not downloaded_img_path:
                logging.error(f"Failed to download image for {asana_id}, skipping")
                return None
            return AsanaImageData(
                id=asana_id,
                name=asana_name,
                img_url=img_url,
                downloaded_img_path=downloaded_img_path,
            )
        except Exception as e:
            logging.error(f"Error processing asana image: {e}")
            return None

    def _extract_asanas_images_data(self, html_content: str) -> list[AsanaImageData]:
        """
        Extracts all asana data using parallel processing.

        Args:
            html_content: The HTML content of the page.

        Returns:
            A list of AsanaImageData dictionaries.
        """
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, "html.parser")
        asana_images = soup.find_all(["img"])
        asanas_images_data: list[AsanaImageData] = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_asana = {
                executor.submit(self._extract_single_asana_image_data, img): img
                for img in asana_images
            }

            for future in as_completed(future_to_asana):
                try:
                    asana_data = future.result()
                    if asana_data:
                        asanas_images_data.append(asana_data)
                except Exception as e:
                    logging.error(f"Error processing future: {e}")

        return asanas_images_data

    def _download_image(self, image_url: str, asana_id: str) -> str | None:
        """
        Downloads and saves an image.

        Args:
            image_url: The URL of the image to download.
            asana_id: The ID of the asana.

        Returns:
            The path to the downloaded image or None if the image is not downloaded.
        """
        try:
            response = self.session.get(image_url)
            response.raise_for_status()

            filename = f"{asana_id}.png"
            filepath = os.path.join(self.images_output_dir, filename)

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

    def _export_data_to_json(self) -> None:
        """
        Exports asana data to JSON file. The JSON file is saved in the output directory with
        the name defined in the output directory.
        """
        json_path = os.path.join(self.output_dir, "asanas.json")
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(self.asanas_images_data, f, indent=2, ensure_ascii=False)
            logging.info(f"Successfully exported data to {json_path}")
        except Exception as e:
            logging.error(f"Error exporting JSON data: {e}")
