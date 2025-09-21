import json
import difflib
from typing import List
from pathlib import Path
from src.types.asana_types import AsanaImageData, ProcessedAsana


class AsanaProcessor:
    def __init__(self, max_similar: int = 4):
        """Initialize the processor with configuration.

        Args:
            max_similar: Maximum number of similar asanas to find for each asana.
        """
        self.max_similar = max_similar

    def process_asanas(self, input_file: str, output_file: str | None = None) -> None:
        """Process asanas to add similar asanas.

        Args:
            input_file: Path to input JSON file containing scraped asanas.
            output_file: Path to output JSON file. If None, will use input_file with _processed suffix.
        """
        # Load asanas
        asanas = self._load_asanas(input_file)

        # Process each asana
        processed_asanas = self._process_asanas(asanas)

        # Determine output file
        if output_file is None:
            input_path = Path(input_file)
            output_file = str(
                input_path.parent / f"{input_path.stem}_processed{input_path.suffix}"
            )

        # Save processed asanas
        self._save_asanas(processed_asanas, output_file)

    def _load_asanas(self, file_path: str) -> List[AsanaImageData]:
        """Load asanas from JSON file."""
        with open(file_path, "r") as f:
            data: List[AsanaImageData] = json.load(f)
            return data

    def _find_similar_asanas(
        self, target_asana: AsanaImageData, all_asanas: List[AsanaImageData]
    ) -> List[str]:
        """Find asanas with similar names, excluding the target asana itself."""
        target_name = target_asana["name"].lower()

        # Create a list of (similarity_ratio, asana_id) tuples
        similarities = []
        for asana in all_asanas:
            if asana["id"] == target_asana["id"]:
                continue

            # Calculate similarity ratio using difflib
            similarity = difflib.SequenceMatcher(
                None, target_name, asana["name"].lower()
            ).ratio()

            # Add extra weight for asanas that share common prefixes
            # This helps group variations of the same pose (e.g., Paschimattanasana A,B,C,D)
            base_name = target_name.split("-")[0]
            other_base = asana["name"].lower().split("-")[0]
            if base_name == other_base:
                similarity += 0.2  # Boost similarity for asanas with same base name

            similarities.append((similarity, asana["id"]))

        # Sort by similarity ratio and get the top matches
        similarities.sort(reverse=True)
        return [asana_id for _, asana_id in similarities[: self.max_similar]]

    def _process_asanas(self, asanas: List[AsanaImageData]) -> List[ProcessedAsana]:
        """Process each asana to add similar asanas."""
        processed: List[ProcessedAsana] = []

        for asana in asanas:
            similar_asanas = self._find_similar_asanas(asana, asanas)
            processed_asana = ProcessedAsana(
                id=asana["id"],
                name=asana["name"],
                img_url=asana["img_url"],
                downloaded_img_path=asana["downloaded_img_path"],
                similar_asanas=similar_asanas,
            )
            processed.append(processed_asana)

        return processed

    def _save_asanas(self, asanas: List[ProcessedAsana], output_file: str) -> None:
        """Save processed asanas to JSON file."""
        with open(output_file, "w") as f:
            json.dump(asanas, f, indent=2)
