from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from time import time
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
path_to_extension = f'{dir_path}\\adblock'


def wait_for(by: By, value: str, driver: WebDriver) -> WebElement:
    return WebDriverWait(driver, 6).until(EC.presence_of_element_located((by, value)))


def setup_driver():
    options = Options()
    options.add_argument('load-extension=' + path_to_extension)
    options.add_argument("--headless")
    options.add_argument("--mute-audio")
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1080, 800)
    return driver


async def create_room(video_link: str, driver: WebDriver, channel):
    from_cda = 'cda.pl' in video_link

    if from_cda:
        video_link = get_video_link_from_cda(video_link, driver)

    driver.get("https://w2g.tv")

    btn_agree = wait_for(By.XPATH, '//*[@id="qc-cmp2-ui"]/div[2]/div/button[2]', driver)
    # Sometimes adblock removes the button before its clicked
    try:
        btn_agree.click()
    except:
        pass

    btn_create = driver.find_element_by_id('create_room_button')
    btn_create.click()

    label_name = driver.find_element_by_id('intro-nickname')
    label_name.clear()
    label_name.send_keys('Bot')

    btn_join = driver.find_element_by_xpath("//div[@class='ui fluid green cancel button']")
    btn_join.click()

    await channel.send(driver.current_url)

    search_bar = driver.find_element_by_id('search-bar-input')
    search_bar.send_keys(video_link)
    search_bar.send_keys(Keys.ENTER)

    pause_menu = wait_for(By.XPATH, "//div[@class='ui inverted tiny menu']", driver)
    btn_pause = pause_menu.find_elements_by_tag_name("a")[0]
    while True:
        state_icon = btn_pause.find_elements_by_tag_name("i")[0].get_attribute('class')
        if state_icon == 'pause icon':
            break
        sleep(0.3)

    search_result = wait_for(By.XPATH, '//*[@id="w2g-search-results"]/div[3]/div/div[1]', driver)
    search_result.click()

    # Doesn't work on cda videos
    if not from_cda:
        # Waits for the timer to go over 1s, then stops the video
        while True:
            video_timer = wait_for(By.XPATH, '//*[@id="player-time"]/span', driver)
            if int(video_timer.text[-2:]) >= 1:
                break
            sleep(0.5)

        action = ActionChains(driver)
        action.move_to_element(btn_pause)
        action.click()
        action.perform()

    # Waits until first watcher joins the room
    while True:
        users = driver.find_elements_by_xpath(
            "//div[@class='w2g-user available animate__animated animate__bounceIn animate__fast']")
        if len(users) >= 1:
            break
        sleep(0.3)

    sleep(2)
    driver.close()


def get_video_link_from_cda(video_link: str, driver: WebDriver):
    driver.get(video_link)
    return driver.find_element_by_tag_name("video").get_attribute('src')


async def run(link: str, channel):
    chromedriver = setup_driver()
    await create_room(link, chromedriver, channel)


if __name__ == "__main__":
    yt_link = 'https://www.youtube.com/watch?v=DLzxrzFCyOs'
    cda_link = 'https://www.cda.pl/video/67833141f'
    run(cda_link)
