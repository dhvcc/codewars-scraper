from os import mkdir
from os.path import isdir, join
from typing import Dict, List, NoReturn

from pathvalidate import sanitize_filename
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
import json


class Scraper:
    FILE_EXT_MAP = {
        "Python": ".py",
        "Javascript": ".js",
    }

    def __init__(
            self,
            email: str,
            password: str,
            timeout: int = 5,
            driver_path: str = "./chromedriver"
    ):
        self.email = email
        self.password = password
        self.timeout = timeout
        self.driver_path = driver_path
        self.driver = webdriver.Chrome(self.driver_path)

        # { Lang: { kyu: { title: code } } }
        self.solutions_data: Dict[str, Dict[str, Dict[str, str]]] = {}

    @property
    def json(self):
        return json.dumps(self.solutions_data, indent=4)

    def scroll_down(self) -> NoReturn:
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight-1000);")
            # Wait to load the page.
            self.driver.implicitly_wait(self.timeout)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def parse_solutions(self, solutions: List[WebElement]) -> NoReturn:
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
        self.driver.get("https://www.codewars.com/users/sign_in")
        email = self.driver.find_element_by_id("user_email")
        password = self.driver.find_element_by_id("user_password")

        email.send_keys(self.email)
        password.send_keys(self.password)

        password.send_keys(Keys.RETURN)
        self.driver.implicitly_wait(self.timeout)

        profile_link = self.driver.find_element_by_id("header_profile_link").get_attribute("href")
        self.driver.get(f"{profile_link}/completed_solutions")

        self.scroll_down()

        solutions = self.driver.find_elements_by_class_name("solutions")
        self.parse_solutions(solutions)

    def save(self) -> NoReturn:
        for lang, kyu_data in self.solutions_data.items():
            if not isdir(lang):
                mkdir(lang)

            for kyu, solutions in kyu_data.items():
                kyu_dir = join(lang, kyu)
                if not isdir(kyu_dir):
                    mkdir(kyu_dir)

                for title, code in solutions.items():
                    filename = f"{sanitize_filename(title)}{self.FILE_EXT_MAP[lang]}"
                    with open(join(kyu_dir, filename), "w+") as kata_file:
                        kata_file.write(code)
                        kata_file.write("\n")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()
