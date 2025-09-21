import argparse
from src.scraping.scrapper import (
    AshtangaAsanasScraper,
    DEVVYOGA_URL,
    DEVVYOGA_FOLDER_HINT_NAMES,
)
from src.processing.processor import AsanaProcessor


def main() -> None:
    parser = argparse.ArgumentParser(description="Ashtanga Yoga Asanas Tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Scraper command
    scraper_parser = subparsers.add_parser(
        "scrape", help="Scrape asanas from Devvrat Yoga website"
    )
    scraper_parser.add_argument(
        "--output-dir",
        default="data/asanas",
        help="Output directory. Defaults to data/asanas.",
    )
    scraper_parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Maximum number of workers. Defaults to 4.",
    )

    # Processor command
    processor_parser = subparsers.add_parser(
        "process", help="Process asanas to add similar asanas"
    )
    processor_parser.add_argument(
        "--input_file",
        default="data/asanas/asanas.json",
        help="Path to input JSON file. Defaults to data/asanas/asanas.json.",
    )
    processor_parser.add_argument(
        "--output-file",
        default=None,
        help="Path to output JSON file. Defaults to input_file with _processed suffix.",
    )
    processor_parser.add_argument(
        "--max-similar",
        type=int,
        default=4,
        help="Maximum number of similar asanas. Defaults to 4.",
    )

    args = parser.parse_args()

    if args.command == "scrape":
        scraper = AshtangaAsanasScraper(
            output_dir=args.output_dir,
            max_workers=args.max_workers,
            url=DEVVYOGA_URL,
            folder_hint_names=DEVVYOGA_FOLDER_HINT_NAMES,
        )
        scraper.scrape_and_export_asanas()
    elif args.command == "process":
        processor = AsanaProcessor(max_similar=args.max_similar)
        processor.process_asanas(args.input_file, args.output_file)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
