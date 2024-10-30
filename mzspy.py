from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import pytz
import mzcommon as mzc
import mzdeclaration as mzd
import time
import sys
import math
import xml.etree.ElementTree as ET
import re
from lxml import html

# Start of Program    

logFile = mzc.open_log_file('mzspy')

mzc.write_log('Start Process', 'W' )

mzc.write_log('Get teams for spy', 'W')

teams = []
try:
    conn, cursor = mzc.db_connect()
    sqlQuery = "SELECT teamid FROM teams;"
    cursor.execute(sqlQuery)

    for row in cursor.fetchall():
        teams.append(row[0])

except:
    sys.exit()

if len(teams) > 0:

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

    for team in teams:
        xmlUrl = 'https://www.managerzone.com/?p=players&tid=' + str(team)
        driver.get(xmlUrl)
        playersContainer = driver.find_elements(By.CLASS_NAME, 'playerContainer')
        sqlQuery = "UPDATE transfers SET teamid = 0 WHERE teamid = %s;"
        values = (team, )
        try:
            cursor.execute(sqlQuery, values)
        except:
            1 == 1

        for playerContainer in playersContainer:
            playerId = int(playerContainer.find_element(By.CLASS_NAME, 'player_id_span').text)
            sqlQuery = "UPDATE transfers SET teamid = %s WHERE id = %s;"
            values = (team, playerId, )
            try:
                cursor.execute(sqlQuery, values)
            except:
                continue
        conn.commit()

else:
    mzc.write_log('No teams to spy', 'W')

driver.close()
driver.quit()

mzc.write_log('End Process', 'W')

