

from selenium import webdriver
from selenium.common.exceptions import WebDriverException

browserHandler = webdriver.Firefox()
browserHandler.get('/home/yash/TechGits/index.html')
try:
    browserHandler.get_screenshot_as_file(yourPathToNewImage)
except WebDriverException:
    print("WebDriverException caught while trying to get a screenshot")
