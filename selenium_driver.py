"""selenium_driver"""
# pylint: disable-msg=too-many-locals
# pylint: disable-msg=too-many-statements
# pylint: disable-msg=line-too-long
# pylint: disable-msg=maybe-no-member
# pylint: disable-msg=import-outside-toplevel
# pylint: disable-msg=too-many-branches
# pylint: disable-msg=wrong-import-order
# pylint: disable-msg=bare-except
# pylint: disable-msg=unnecessary-pass
# pylint: disable-msg=broad-except
# pylint: disable-msg=too-many-nested-blocks
# pylint: disable-msg=logging-fstring-interpolation

import random
import time
from random import uniform
from selenium import webdriver
from selenium_stealth import stealth
from fake_useragent import UserAgent
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def get_driver():
    profile_path = '/where_your_chrome_directory/'

    user_agent = UserAgent().random
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--enable-automation")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins-discovery")
    options.add_argument("--disable-default-apps")
    options.add_argument("--disable-background-networking")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver_service = Service(executable_path='/home/dm/Desktop/bots/python/price/chromedriver')
    driver = webdriver.Chrome(service=driver_service, options=options)

    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            run_on_insecure_origins=True)

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        'source': """
            // Имитация свойств объекта navigator
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            Object.defineProperty(navigator, 'language', {
                get: () => 'en-US'
            });
            Object.defineProperty(navigator, 'platform', {
                get: () => 'Win32'
            });
            
            // Имитация свойств объекта document
            Object.defineProperty(document, 'visibilityState', {
                get: () => 'visible',
                configurable: true
            });
            Object.defineProperty(document, 'hidden', {
                get: () => false,
                configurable: true
            });

            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        """
    })

    time.sleep(uniform(1, 3))

    return driver
