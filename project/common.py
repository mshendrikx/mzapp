from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import os
import time
import pytz
import mysql.connector
import subprocess

def mzdriver(mzuser, mzpass):

    try:       
        options = Options()    
        options.add_argument("start-maximized")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--lang=en")
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options) 
        driver.get('https://www.managerzone.com/?changesport=soccer&lang=en')

    except Exception as e:
        # Driver initlization fails
        return None

    try:
        # Set Username
        element = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.ID, "login_username"))
        )
        element.clear()
        element.send_keys(mzuser)
        # Set Password
        element = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.ID, "login_password"))
        )
        element.clear()
        element.send_keys(mzpass)
    except Exception as e:
        # Missing login fields 
        return None
        
    # Set Cookies
    try: 
        element = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowallSelection"))
            )
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", element)    
        time.sleep(1)
        element.click()
    except Exception as e:
        # Set cookies fails
        return None
    
    try:
    # Login Button
        loginElement = WebDriverWait(driver, 60).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="login"]'))) 
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", element)
        time.sleep(1)     
        loginElement.click()            
    except Exception as e:
        # Login button fails
        return None
    
    return driver
