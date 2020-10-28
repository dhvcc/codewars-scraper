from codewars_scraper.speedups import json
from os import mkdir
from os.path import isdir, join
from typing import Dict, List, NoReturn

from loguru import logger
from pathvalidate import sanitize_filename
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from codewars_scraper import file_extensions


class Scraper:

    def __init__(
            self,
            email: str,
            password: str,
            *,
            headless: bool = True,
            timeout: int = 10,
            driver_path: str = "./codewars_scraper/driver/chromedriver"
    ):
        logger.debug("Scraper init")
        self.email = email
        self.password = password

        self.timeout = timeout

        self.options = webdriver.ChromeOptions()
        self.options.headless = headless

        self.driver_path = driver_path
        self.driver = webdriver.Chrome(executable_path=self.driver_path, options=self.options)

        # { Lang: { kyu: { title: code } } }
        self.solutions_data: Dict[str, Dict[str, Dict[str, str]]] = {}

    @property
    def json(self):
        logger.info("Returning JSON")
        return json.dumps(self.solutions_data, indent=4)

    def scroll_down(self) -> NoReturn:
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        logger.info(f"Scrolling down the page, initial height {last_height}")

        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight-1000);")
            # Wait to load the page.
            self.driver.implicitly_wait(self.timeout)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            logger.debug(f"New height {new_height}")
            if new_height == last_height:
                break
            last_height = new_height

    def parse_solutions(self, solutions: List[WebElement]) -> NoReturn:
        logger.info("Parsing solutions")
        for solution in solutions:
            title_div = solution.find_element_by_class_name("item-title")

            language_header = solution.find_element_by_tag_name("h6")
            kyu_span = title_div.find_element_by_tag_name("span")
            title_anchor = title_div.find_element_by_tag_name("a")
            code_elem = solution.find_element_by_tag_name("code")

            language = language_header.text.rstrip(":")
            kyu = kyu_span.text
            title = title_anchor.text
            code = code_elem.text

            if language in self.solutions_data:
                if kyu in self.solutions_data[language]:
                    self.solutions_data[language][kyu][title] = code
                else:
                    self.solutions_data[language][kyu] = {
                        title: code
                    }
            else:
                self.solutions_data[language] = {
                    kyu: {
                        title: code
                    }
                }

    def parse(self) -> NoReturn:
        logger.info("Parsing started")
        self.driver.get("https://www.codewars.com/users/sign_in")
        email = self.driver.find_element_by_id("user_email")
        password = self.driver.find_element_by_id("user_password")

        email.send_keys(self.email)
        password.send_keys(self.password)

        password.send_keys(Keys.RETURN)
        self.driver.implicitly_wait(self.timeout)

        profile_link = WebDriverWait(
            self.driver, self.timeout
        ).until(
            EC.presence_of_element_located((By.ID, "header_profile_link"))
        ).get_attribute("href")

        self.driver.get(f"{profile_link}/completed_solutions")

        self.scroll_down()

        solutions = self.driver.find_elements_by_class_name("solutions")
        self.parse_solutions(solutions)

    def save(self) -> NoReturn:
        logger.info("Saving")
        for lang, kyu_data in self.solutions_data.items():
            if not isdir(lang):
                mkdir(lang)

            for kyu, solutions in kyu_data.items():
                kyu_dir = join(lang, kyu)
                if not isdir(kyu_dir):
                    mkdir(kyu_dir)

                for title, code in solutions.items():
                    filename = f"{sanitize_filename(title)}{file_extensions.MAP[lang]}"
                    with open(join(kyu_dir, filename), "w+") as kata_file:
                        kata_file.write(code)
                        kata_file.write("\n")

    def __enter__(self):
        logger.debug("Context manager entered")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug("Context manager exited")
        self.driver.quit()
        logger.debug("Driver quit")
