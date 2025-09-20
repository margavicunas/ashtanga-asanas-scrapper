import pytest
import responses
from PIL import Image
from io import BytesIO
import json
import os
from src.scraping.scrapper import AshtangaAsanasScraper
from src.types.asana_types import AsanaImageData


TEST_URL = "https://example.com/ashtanga"
FOLDER_HINT = "uploads/2019/07"


@pytest.fixture
def scraper(temp_output_dir: str) -> AshtangaAsanasScraper:
    return AshtangaAsanasScraper(
        url=TEST_URL, folder_hint_name=FOLDER_HINT, output_dir=temp_output_dir
    )


class TestAshtangaAsanasScraper:
    def test_create_asana_id(self, scraper: AshtangaAsanasScraper) -> None:
        """Test creation of URL-friendly asana IDs."""
        test_cases = [
            ("Test Asana", "test-asana"),
            ("Test@#$Asana", "testasana"),
            ("Test_Asana_1", "test_asana_1"),
            ("  Test  Asana  ", "test-asana"),
        ]

        for input_name, expected_id in test_cases:
            assert scraper._create_asana_id(input_name) == expected_id

    def test_get_asana_name(self, scraper: AshtangaAsanasScraper) -> None:
        """Test extraction of asana names from image metadata."""
        img_with_title = {"title": "Test Title", "alt": "Test Alt", "src": "test.png"}
        assert scraper._get_asana_name(img_with_title) == "Test Title"

        img_with_alt = {"alt": "Test Alt", "src": "test.png"}
        assert scraper._get_asana_name(img_with_alt) == "Test Alt"

        img_with_src = {"src": "path/to/test-asana.png"}
        assert scraper._get_asana_name(img_with_src) == "test-asana"

        img_without_metadata: dict[str, str] = {}
        assert scraper._get_asana_name(img_without_metadata) is None

    @responses.activate
    def test_get_page_content(
        self, scraper: AshtangaAsanasScraper, mock_html_content: str
    ) -> None:
        """Test fetching webpage content."""
        responses.add(responses.GET, TEST_URL, body=mock_html_content, status=200)

        content = scraper._get_page_content()
        assert content == mock_html_content

        responses.reset()
        responses.add(responses.GET, TEST_URL, status=404)
        assert scraper._get_page_content() is None

    @responses.activate
    def test_download_image(self, scraper: AshtangaAsanasScraper) -> None:
        """Test image downloading and processing."""
        test_url = "https://example.com/test.png"
        test_id = "test-asana"

        img = Image.new("RGBA", (100, 100), (255, 0, 0, 128))
        img_byte_arr: BytesIO = BytesIO()
        img.save(img_byte_arr, format="PNG")
        img_byte_arr = img_byte_arr.getvalue()

        responses.add(
            responses.GET,
            test_url,
            body=img_byte_arr,
            status=200,
            content_type="image/png",
        )

        result = scraper._download_image(test_url, test_id)
        assert result is not None
        assert os.path.exists(result)
        assert result.endswith(".png")

        responses.reset()
        responses.add(responses.GET, test_url, status=404)
        assert scraper._download_image(test_url, "error-test") is None

    @responses.activate
    def test_extract_asanas_images_data(
        self, scraper: AshtangaAsanasScraper, mock_html_content: str
    ) -> None:
        """Test extraction of asana data from HTML content."""
        responses.add(
            responses.GET,
            "https://example.com/uploads/2019/07/test-asana.png",
            body=self._create_test_image(),
            status=200,
            content_type="image/png",
        )
        responses.add(
            responses.GET,
            "https://example.com/uploads/2019/07/another-asana.png",
            body=self._create_test_image(),
            status=200,
            content_type="image/png",
        )

        results = scraper._extract_asanas_images_data(mock_html_content)

        assert len(results) == 2
        assert all(isinstance(result, dict) for result in results)
        assert all(
            key in result
            for result in results
            for key in ["id", "name", "img_url", "downloaded_img_path"]
        )

    def test_export_data_to_json(
        self, scraper: AshtangaAsanasScraper, temp_output_dir: str
    ) -> None:
        """Test JSON export functionality."""
        test_data: list[AsanaImageData] = [
            {
                "id": "test-asana",
                "name": "Test Asana",
                "img_url": "https://example.com/test.png",
                "downloaded_img_path": "/path/to/test.png",
            }
        ]
        scraper.asanas_images_data = test_data

        scraper._export_data_to_json()

        json_path = os.path.join(temp_output_dir, "asanas.json")
        assert os.path.exists(json_path)

        with open(json_path, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)

        assert loaded_data == test_data

    def _create_test_image(self) -> bytes:
        """Creates a valid test image in bytes format."""
        img = Image.new("RGB", (100, 100), (255, 255, 255))
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format="PNG")
        return img_byte_arr.getvalue()
