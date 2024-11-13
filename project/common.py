from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import pytz
import mysql.connector
import subprocess

def mz_login(mzuser, mzpass):

    try:       
        ChromeDriverManager().install()
        options = Options()    
        options.add_argument("start-maximized")
        #options.add_argument("disable-infobars")
        #options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--lang=en")
        options.add_argument("--remote-debugging-port=9222") 
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options) 
        driver.get('https://www.managerzone.com/?changesport=soccer&lang=en')

    except Exception as e:
        # Driver initlization fails
        return e, 1

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
        return e, 2
        
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
        return e, 3
    
    time.sleep(3)

    try:
    # Login Button
        loginElement = WebDriverWait(driver, 60).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="login"]'))) 
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", element)
        time.sleep(1)     
        loginElement.click()            
    except Exception as e:
        # Login button fails
        return e, 4
    
    time.sleep(5)

    return driver, 0

def db_connect():

    count = 0
    connOk = False
    while connOk == False:
        count += 1
        try:
            conn = mysql.connector.connect(
                user=os.environ.get("MZDBUSER"), password=os.environ.get("MZDBUSER"), host=os.environ.get("MZDBHOST"), database=os.environ.get("MZDBNAME"))
            cursor = conn.cursor(buffered=True)
            connOk = True
        except:
            conn = None
            cursor = None
            if count > 120:
                connOk = True                
            else:
                time.sleep(5)

    return conn, cursor

def time_now(type):

    nowUtc = datetime.utcnow()
    nowUtc = nowUtc.replace(tzinfo=pytz.utc)
    nowBr = nowUtc.astimezone(pytz.timezone(os.environ.get("MZ_TZ")))
    if type == 'S':
        return nowBr.strftime('%Y/%m/%d-%H:%M')
    elif type == 'N':
        return nowBr.strftime('%Y%m%d%H%M')
    elif type == 'I':
        return int(nowBr.strftime('%Y%m%d%H%M'))
    else:
        return nowBr

def open_log_file(name):

    nowBrStr = time_now('N')
    mzd.LOG_FILE = mzd.LOG_LOCATION + name + '_' + nowBrStr[0:8] + '_' + mzd.MZREGION + '.log'

    return mzd.LOG_FILE

def write_log(message, messType):
    
    writeLog = False
    displayLog = False
    
    if messType in mzd.MZMESSAGE and 'F' in mzd.MZMESSAGE:
        writeLog = True
    if messType in mzd.MZMESSAGE and 'P' in mzd.MZMESSAGE:
        displayLog = True
    
    if writeLog == True or displayLog == True:
        logLine = messType + ' ' + time_now('S') + ' ' + message
    else:
        return
    if writeLog == True:
        logFile = open(mzd.LOG_FILE, 'a')
        logFile.write(logLine)
        logFile.write('\n')   
        logFile.close()
    if displayLog == True:
        print(logLine)

def get_countries(cursor):

    countries = []

    cursor.execute("SELECT * FROM countries")
    for countryRow in cursor.fetchall():
        countries.append(countryRow)

    return countries

def only_numerics(seq):
    seq_type= type(seq)
    return seq_type().join(filter(seq_type.isdigit, seq))

def get_deadline_ctrl_dt():

    spTzone = pytz.timezone('America/Sao_Paulo')

    connLocal, cursorLocal = db_connect()
    try:
        cursorLocal.execute('SELECT deadline FROM mzctrl WHERE id = "MZCTRL"')
        dt = datetime.strptime(cursorLocal.fetchall()[0], '%Y/%m/%d-%I:%M%')
        dt = spTzone.localize(dt)
    except:
        dt = None
    
    connLocal.close()

    return dt

def update_transf_ind(conn, cursor):

    nowBrStr = time_now('I')

    cursor.execute('''
    UPDATE transfers
       SET onmarket = ' '
     WHERE onmarket = 'X' 
       AND deadline < %s ;
    ''', (nowBrStr,))

    conn.commit()