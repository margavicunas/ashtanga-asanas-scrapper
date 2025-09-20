from src.scraping.scrapper import AshtangaAsanasScraper

URL = "https://www.devvratyoga.com/learning-resources/ashtanga-yoga-asanas-with-names-images/"
FOLDER_HINT_NAME = "uploads/2019/07/"


def main() -> None:
    ashtanga_asanas_scraper = AshtangaAsanasScraper(URL, FOLDER_HINT_NAME)
    ashtanga_asanas_scraper.scrape_and_export_asanas()


if __name__ == "__main__":
    main()
