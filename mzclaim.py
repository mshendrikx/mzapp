from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import mzcommon as mzc
import mzdeclaration as mzd
import time
import pytz
import sys

def db_claim_lock(value, conn, cursor):

    sqlQuery = "UPDATE mzctrl SET claimctrl=%s WHERE id = 'MZCTRL';"
    values = (value, )
    cursor.execute(sqlQuery, values)
    conn.commit()

def claim_prize(driver):
    
    localRet = 'OK'

    try:
        driver.get('https://www.managerzone.com/?p=event')

        time.sleep(5)
        claimPrize = driver.find_element(By.XPATH, '/html/body/div[3]/div[3]/div[3]/div[2]/div[2]/div/div[2]/div[1]/div/div[2]/a')
        claimPrize.click()
        time.sleep(5) 

        driver.get('https://www.managerzone.com/?p=event')
        claimPrize = driver.find_element(By.XPATH, '/html/body/div[3]/div[3]/div[3]/div[2]/div[2]/div/div[2]/div[1]/div/div[2]/a')
        claimClass = claimPrize.get_attribute("class")
        if claimClass != 'mzbtn buttondiv_disabled button_account':
            localRet = 'NO'

    except:
        localRet = 'NO'
    
    return localRet


# Start of Program    

logFile = mzc.open_log_file('mzclaim')

mzc.write_log('Start Process', 'W' )

#mzd.MZVDISPLAY = True

#display = mzc.virtual_display()

conn, cursor = mzc.db_connect()

sqlQuery = "SELECT claimctrl, nextclaim FROM mzctrl WHERE id = 'MZCTRL';"
cursor.execute(sqlQuery)
selRow = cursor.fetchone()
claimBlock = int(selRow[0])
nextClaim = int(selRow[1])

if claimBlock == 1:
    mzc.write_log('mzclaim alredy in execution', 'W')
    mzc.write_log('End Process', 'W')
    sys.exit()

nowUtc = datetime.utcnow()
nowUtc = nowUtc.replace(tzinfo=pytz.utc)
nowBr = nowUtc.astimezone(pytz.timezone(mzd.MZ_TZ))
nowBrInt = int(nowBr.strftime('%Y%m%d%H%M'))

if nowBrInt < nextClaim:
    mzc.write_log('mzclaim not in claim period', 'W')
    mzc.write_log('End Process', 'W')
    sys.exit()

db_claim_lock(1, conn, cursor)

mzc.write_log('Login Process', 'W')

driverError = 99
loginCount = 0
while driverError > 0:

    driver, driverError = mzc.mz_login('mshendrikx', '049sajh', False, True, False)
    if driverError == 0:
        mzc.write_log('Successful login into managerzone.com', 'S')
    elif driverError == 1:
        mzc.write_log('Driver initlization fails', 'E')
        mzc.write_log(f"Tipo da exceção: {type(driver)}", 'E')
        mzc.write_log(f"Mensagem de erro: {driver}", 'E')
        mzc.write_log(f"Traceback: {driver.__traceback__}", 'E')
    elif driverError == 2:
        mzc.write_log('Missing login fields', 'E')
    elif driverError == 3:
        mzc.write_log('Set cookies fails', 'E')
    elif driverError == 4:
        mzc.write_log('Login button fails', 'E')

    if driverError > 0:
        time.sleep(1)

    loginCount += 1

    if loginCount > 20:
        mzc.write_log('Cant login in magerzone.com', 'E')
        db_claim_lock(0, conn, cursor)
        sys.exit()

# Friendly Book
mzc.write_log('Claim Prize', 'W')
claimPrize = claim_prize(driver)

if claimPrize == 'OK':
    mzc.write_log('Claim Prize OK', 'W')
    nowUtc = datetime.utcnow()
    nowUtc = nowUtc.replace(tzinfo=pytz.utc)
    nowBr = nowUtc.astimezone(pytz.timezone(mzd.MZ_TZ))
    time_change = timedelta(minutes=242)
    maxDate = nowBr + time_change
    nextClaim = int(maxDate.strftime('%Y%m%d%H%M'))
    
    sqlQuery = "UPDATE mzctrl SET nextclaim=%s WHERE id = 'MZCTRL';"
    values = (nextClaim, )
    cursor.execute(sqlQuery, values)
    conn.commit()

else:
    mzc.write_log('Claim Prize Fails', 'E')

db_claim_lock(0, conn, cursor)

mzc.write_log('End Process', 'W')
