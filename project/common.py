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
import smtplib
import random
import pandas as pd

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .models import User, Updates, Mzcontrol, Player, Countries

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from project import db

def only_numerics(seq):
    seq_type= type(seq)
    return seq_type().join(filter(seq_type.isdigit, seq))

def mzdriver(mzuser=os.environ.get("MZUSER"), mzpass=os.environ.get("MZPASS")):

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

# Recover password
def recover_email(user, password):

    # Example usage with a custom sender name
    sender_name = "MZApp"
    sender_email = os.environ["MZAPP_EMAIL"]
    recipient_email = user.email
    subject = "MZApp Login"
    text_content = "User: " + str(user.email) + "\n" + "Password: " + str(password)

    return send_email(
        sender_name=sender_name,
        sender_email=sender_email,
        recipient=recipient_email,
        subject=subject,
        text_content=text_content,
        smtp_server=os.environ["SMTP_SERVER"],
        smtp_port=os.environ["SMTP_PORT"],
    )
    
def send_email(
    sender_name,
    sender_email,
    recipient,
    subject,
    text_content,
    html_content=None,
    smtp_server="localhost",
    smtp_port=25,
):
    message = create_message(
        sender_name, sender_email, recipient, subject, text_content, html_content
    )

    try:
        # Connect to the SMTP server (modify server/port as needed)
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            # Start TLS encryption if required by Postfix configuration
            if server.has_extn("STARTTLS"):
                server.starttls()

            # Authenticate if required (check Postfix configuration)
            if server.has_extn("AUTH"):
                # Replace with your credentials
                server.login("your_username", "your_password")

            server.sendmail(sender_email, recipient, message.as_string())

            return True
    except:
        return False


def create_message(
    sender_name, sender_email, recipient, subject, text_content, html_content=None
):
    message = MIMEMultipart("alternative")
    message["From"] = (
        sender_name + " <" + sender_email + ">"
    )  # Set sender name and email
    message["To"] = recipient
    message["Subject"] = subject

    # Add plain text part
    part1 = MIMEText(text_content, "plain")
    message.attach(part1)

    # Add HTML part (optional)
    if html_content:
        part2 = MIMEText(html_content, "html")
        message.attach(part2)

    return message

def get_distinct_numbers_random(start, end):
    """Generates a list of distinct numbers between start and end in random order.

    Args:
        start: The starting number.
        end: The ending number.

    Returns:
        A list of distinct numbers in random order.
    """

    num_set = set(range(start, end + 1))
    random_numbers = random.sample(num_set, len(num_set))
    return random_numbers

def update_countries():

    db = get_db()
    
    driver = mzdriver()
    if driver == None:
        return None
    driver.get('https://www.managerzone.com/?p=national_teams&type=senior')
    selCountry = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, "cid")))
    countries_sel = selCountry.find_elements(By.TAG_NAME, 'option')
    countries = []
    for country_sel in countries_sel:
        country = []
        country.append(country_sel.get_attribute('value'))
        country.append(country_sel.text)
        countries.append(country)
    driver.get('https://www.managerzone.com/?p=rank&sub=countryrank')
    driver.get('https://www.managerzone.com/?p=rank&sub=countryrank')
    countryRankTable = driver.find_element(By.XPATH, '//*[@id="countryRankTable"]/tbody')
    countryRankTable = countryRankTable.find_elements(By.TAG_NAME, 'tr')
    flagsData = []
    for countryRank in countryRankTable:
        flagData = []
        countryData = countryRank.find_elements(By.TAG_NAME, 'td')
        flagData.append(countryData[2].text)
        flagData.append(countryData[3].find_element(By.TAG_NAME, 'img').screenshot_as_base64)
        flagsData.append(flagData)
    flagsArray = pd.DataFrame(flagsData, columns=['name', 'image'])
    flagsArray = flagsArray.set_index('name')
    for country in countries:
        try:
            countryID = int(country[0])
            countryName = country[1]
            countryImage = flagsArray.loc[countryName].image
        except:
            msgLog = 'Fail to get data for country: ' + countryName 
            continue
        
        country = db.query(Countries).filter_by(id=countryID).first()
        if country:
            country.name = countryName
            country.flag = countryImage
        else:
            new_country = Countries(
                id=countryID,
                name = countryName,
                flag = countryImage,            
            )
            db.add(new_country)
    db.commit()
    driver.close()       
    db.close()
    
def control_data():
    
#    db = get_db()

    driver = mzdriver()
    if driver == None:
        return None
    driver.get('https://www.managerzone.com/?p=clubhouse')
    seasonInfo = WebDriverWait(driver, 30).until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="header-stats-wrapper"]/h5[3]')))
    season = int(only_numerics(seasonInfo.text.split('·')[0]))
    mzcontrol = db.query(Mzcontrol).first()
    old_season = mzcontrol.season
    mzcontrol.season = season
    db.commit()
    if season != old_season:
        players = db.query(Player).all()
        for player in players:
            player.age = season - player.season
    db.commit()
    driver.close()
#    db.close()
   
def get_db():
    
    mariadb_pass = os.environ.get("MZDBPASS")
    mariadb_host = os.environ.get("MZDBHOST")
    mariadb_database = os.environ.get("MZDBNAME")
    
    sql_text = "mysql+pymysql://root:" + mariadb_pass + "@" + mariadb_host + "/" + mariadb_database
    
    engine = create_engine(sql_text)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    return db