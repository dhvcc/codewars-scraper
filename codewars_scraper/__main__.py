from argparse import ArgumentParser
from os import environ

from loguru import logger

from codewars_scraper import Scraper


# TODO: Add output path


def arguments():
    parser = ArgumentParser()
    parser.add_argument(
        "--path", help="save solutions to {path} instead of current directory", type=str
    )
    parser.add_argument(
        "--json", help="print solutions in json format", action="store_true"
    )
    parser.add_argument(
        "--no-headless", help="disable headless mode", action="store_true"
    )
    parser.add_argument(
        "--timeout",
        help="customize selenium timeout (if network is slow)",
        type=int,
        default=10,
    )
    args = parser.parse_args()
    return args


def scrape(args, email: str, password: str):
    logger.info("Starting to scrape")
    with Scraper(
        email, password, headless=not args.no_headless, timeout=args.timeout
    ) as scraper:
        scraper.parse()
        if args.path:
            scraper.save((args.path or "") + "/")
        elif args.json:
            print(scraper.json)


def main():
    email = environ.get("CODEWARS_EMAIL")
    password = environ.get("CODEWARS_PASSWORD")

    if not email or not password:
        raise Exception(
            "Environment variables CODEWARS_EMAIL and CODEWARS_PASSWORD are required"
        )

    args = arguments()

    if args.json:
        if args.path:
            logger.warning("JSON output will be ignored because --path was provided")
        else:
            logger.remove()

    logger.catch(scrape)(args, email, password)


if __name__ == "__main__":
    main()
