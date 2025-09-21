import json
import difflib
from typing import List
from src.types.asana_types import AsanaImageData, ProcessedAsana

EXTRA_BOOST_SIMILARITY_RATIO = 0.2


def load_asanas(file_path: str) -> List[AsanaImageData]:
    """Load asanas from JSON file."""
    with open(file_path, "r") as f:
        data: List[AsanaImageData] = json.load(f)
        return data


def find_similar_asanas(
    target_asana: AsanaImageData, all_asanas: List[AsanaImageData], max_similar: int = 4
) -> List[str]:
    """Find asanas with similar names, excluding the target asana itself."""
    target_name = target_asana["name"].lower()
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
            similarity += EXTRA_BOOST_SIMILARITY_RATIO

        similarities.append((similarity, asana["id"]))

    similarities.sort(reverse=True)
    return [asana_id for _, asana_id in similarities[:max_similar]]


def process_asanas(
    input_file: str = "asanas.json", output_file: str = "asanas_processed.json"
) -> None:
    """Process asanas to add similar poses."""
    asanas = load_asanas(input_file)

    processed_asanas = []
    for asana in asanas:
        processed_asana = ProcessedAsana(
            id=asana["id"],
            name=asana["name"],
            img_url=asana["img_url"],
            downloaded_img_path=asana["downloaded_img_path"],
            similar_poses=find_similar_asanas(asana, asanas),
        )
        processed_asanas.append(processed_asana)

    with open(output_file, "w") as f:
        json.dump(asanas, f, indent=2)
