from argparse import ArgumentParser
from os import environ

from loguru import logger

from codewars_scraper import Scraper

# TODO: Add output path

EMAIL = environ.get("CODEWARS_EMAIL")
PASSWORD = environ.get("CODEWARS_PASSWORD")


@logger.catch
def main():
    logger.info("Starting to scrape")
    with Scraper(EMAIL, PASSWORD,
                 headless=not args.debug,
                 timeout=args.timeout) as scraper:
        scraper.parse()
        if args.save:
            scraper.save()
        if args.json:
            print(scraper.json)


if __name__ == '__main__':
    if not EMAIL or not PASSWORD:
        raise Exception("Environment variables CODEWARS_EMAIL and CODEWARS_PASSWORD are required")

    parser = ArgumentParser()
    parser.add_argument("--save",
                        help="save solutions in current directory",
                        action="store_true")
    parser.add_argument("--json",
                        help="print solutions in json format",
                        action="store_true")
    parser.add_argument("--debug",
                        help="debug mode, disables headless mode",
                        action="store_true")
    parser.add_argument("--timeout",
                        help="customize selenium timeout (if network is slow)",
                        type=int,
                        default=10)
    args = parser.parse_args()

    if args.json:
        # TODO: mute output, except json
        ...
    if args.debug:
        # TODO: set loguru level to debug
        ...

    main()
