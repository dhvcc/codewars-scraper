from codewars_scraper import Scraper

# TODO: Add metadata
# TODO: Add loguru logging
# Poetry?
# TODO: Speedups (json)
# TODO: Updated extension map

# TODO: Config management
# TODO: Make executable
# TODO: Add output path

EMAIL = ""
PASSWORD = ""

with Scraper(EMAIL, PASSWORD) as scraper:
    scraper.parse()
    scraper.save()
