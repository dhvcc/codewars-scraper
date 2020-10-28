from loguru import logger

from codewars_scraper import Scraper

# TODO: Config management
# TODO: Make executable
# TODO: Add output path

EMAIL = ""
PASSWORD = ""


@logger.catch
def main():
    logger.info("Starting to scrape")
    with Scraper(EMAIL, PASSWORD, headless=True) as scraper:
        scraper.parse()
        scraper.save()


if __name__ == '__main__':
    main()
