import argparse
from src.scraping.scrapper import AshtangaAsanasScraper, DEVVYOGA_URL, DEVVYOGA_FOLDER_HINT_NAME


def main() -> None:
    parser = argparse.ArgumentParser(description="Ashtanga Yoga Asanas Tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Scraper command
    scraper_parser = subparsers.add_parser("scrape", help="Scrape asanas from Devvrat Yoga website")
    scraper_parser.add_argument(
        "--output-dir", default="data/asanas", help="Output directory. Defaults to data/asanas."
    )
    scraper_parser.add_argument(
        "--max-workers", type=int, default=4, help="Maximum number of workers. Defaults to 4."
    )
    )

    args = parser.parse_args()

    if args.command == "scrape":
        scraper = AshtangaAsanasScraper(
            output_dir=args.output_dir,
            max_workers=args.max_workers,
            url=DEVVYOGA_URL,
            folder_hint_name=DEVVYOGA_FOLDER_HINT_NAME,
        )
        scraper.scrape_and_export_asanas()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
