from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import mzcommon as mzc
import mzdeclaration as mzd
import datetime
import time
import sys

def get_tactic():

    sqlQuery = "SELECT weekDay FROM mzctrl WHERE id = 'MZCTRL'"
    
    weekDay = datetime.datetime.today().weekday()
    
    if weekDay == 6 or weekDay == 5:
        dayStr = 'montactic'
    elif weekDay == 0:
        dayStr = 'tuetactic'
    elif weekDay == 1 or weekDay == 2:
        dayStr = 'thutactic'
    elif weekDay == 3:
        dayStr = 'fritactic'
    elif weekDay == 4:
        dayStr = 'sattactic'
        
    sqlQuery = sqlQuery.replace("weekDay", dayStr)
    
    try:
        conn, cursor = mzc.db_connect()
        cursor.execute(sqlQuery)
    
        for row in cursor.fetchall():
            taticValue = row[0]
            break

        conn.close()
    except:
        return 'z'
    
    return taticValue
    
    
def friendly_book(driver, taticValue):
    
    try:
        driver.get('https://www.managerzone.com/?p=challenges&tab=quick')

        optIn = WebDriverWait(driver, 30).until(
                            EC.presence_of_element_located((By.ID, 'qc-opt-in')))

        taticHome = Select(driver.find_element(By.ID, "tactic_home"))
        taticAway = Select(driver.find_element(By.ID, "tactic_away"))

        taticHome.select_by_value(taticValue)
        taticAway.select_by_value(taticValue)

        optIn = driver.find_element(By.ID, 'qc-opt-in')
        optIn.click()
        time.sleep(10)        

    except:
        return 'NO'
    
    return 'OK'


# Start of Program    

logFile = mzc.open_log_file('mzfriendly')

mzc.write_log('Start Process', 'W' )

#display = mzc.virtual_display()

mzc.write_log('Login Process', 'W')

tacticValue = get_tactic()

if tacticValue == 'z':
    mzc.write_log('No tactic defined', 'E')
    sys.exit()   

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
        sys.exit()

if driver == None:
    mzc.write_log('Login Fails', 'E')
    sys.exit()

# Friendly Book
mzc.write_log('Friendly Book', 'W')
friendlyBook = friendly_book(driver, tacticValue)

if friendlyBook == 'OK':
    mzc.write_log('Friendly Book OK', 'W')
else:
    mzc.write_log('Friendly Book Fails', 'E')

driver.close()
driver.quit()

mzc.write_log('End Process', 'W')
