from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


def start_selenium_to_create_session():
    driver = webdriver.Chrome()

    driver.get('http://www.jcc.state.fl.us/JCC/searchJCC/searchCases.asp')
    print('[x] Search Form Opened')
    # fill the form
    start_date = driver.find_element(By.NAME, 'DateOpenStart')
    end_date = driver.find_element(By.NAME, 'DateOpenEnd')
    start_date.send_keys('01/01/2010')
    end_date.send_keys('05/05/2022')
    dropdown = driver.find_element(By.NAME, "CaseStatus")
    select = Select(dropdown)
    select.select_by_visible_text("Inactive")
    submit_button = driver.find_element(By.NAME, 'submit')
    print('[x] Submitting form data please wait it take some minutes')
    submit_button.click()
    # get browser session data and continue with scrappy
    cookies = driver.get_cookies()
    driver.quit()
    print('[x] Session Created ')
    return cookies
