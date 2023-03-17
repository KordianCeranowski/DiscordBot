from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


def get_subtitles(query: str):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    with webdriver.Chrome(options=options) as driver:
        driver.get("https://www.opensubtitles.org")

        search_bar = driver.find_element_by_xpath("//*[@id=\"search_text\"]")
        search_bar.send_keys(query)
        language = driver.find_element_by_xpath("/html/body/div[1]/div[7]/form/div[1]/button")
        language.click()
        english = [element for element in driver.find_elements_by_tag_name("span") if element.text == "English"][0]
        english.click()
        search_bar.send_keys(Keys.ENTER)

        download = [element for element in driver.find_elements_by_tag_name("a") if element.text == "Download"][0]
        link = download.get_attribute("href")
        return link
