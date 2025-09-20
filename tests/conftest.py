import pytest
import os
import shutil
from pathlib import Path
from typing import Generator


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Generator[str, None, None]:
    """Creates a temporary directory for test outputs."""
    output_dir = str(tmp_path / "test_asanas")
    os.makedirs(output_dir, exist_ok=True)
    yield output_dir
    shutil.rmtree(output_dir)


@pytest.fixture
def mock_html_content() -> str:
    """Returns mock HTML content for testing."""
    return """
    <html>
        <body>
            <img src="https://example.com/uploads/2019/07/test-asana.png"
                 alt="Test Asana"
                 title="Test Asana Title"/>
            <img src="https://example.com/uploads/2019/07/another-asana.png"
                 alt="Another Asana"/>
            <img src="https://example.com/not-an-asana.png"
                 alt="Not an Asana"/>
        </body>
    </html>
    """


@pytest.fixture
def mock_image_content() -> bytes:
    """Returns mock image content for testing."""
    return b"Mock image content"
