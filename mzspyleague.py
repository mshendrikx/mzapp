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
from bs4 import BeautifulSoup

def add_teams(driver, conn, cursor, leagues):

    teams = []
    for league in leagues:

        leagueDesc = league[1]
        url = 'http://www.managerzone.com/xml/team_league.php?sport_id=1&league_id=' + str(league[0])
        driver.get(url)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        soupText = soup.text

        soupText = soupText.replace('teamId="', 'zz__mark1') 
        soupText = soupText.replace('" teamName="', 'zz__mark2') 
        soupText = soupText.replace('" teamShortname=', 'zz__mark3') 

        foundIds = re.findall(r"zz__mark1(.*?)zz__mark2", soupText)
        foundNames = re.findall(r"zz__mark2(.*?)zz__mark3", soupText)

        counter = 0
        while counter < 12:
            teamId = foundIds[counter]
            teamName = foundNames[counter]
            counter += 1
            try:
                cursor.execute("""
                REPLACE INTO teams (
                teamid,
                name,
                leaguedesc)
                VALUES (%s,%s,%s)
                """, (
                    teamId,
                    teamName,
                    leagueDesc))

                teams.append(teamId)

            except:
                continue

    conn.commit()

    return teams

# Start of Program    

logFile = mzc.open_log_file('mzspyleague')

mzc.write_log('Start Process', 'W' )

mzc.write_log('Get teams for spy', 'W')

leagues = []

try:
    conn, cursor = mzc.db_connect()

    sqlQuery = "UPDATE transfers SET teamid = 0;"
    cursor.execute(sqlQuery)

    sqlQuery = "SELECT * FROM leagues;"
    cursor.execute(sqlQuery)

    for row in cursor.fetchall():
        leagues.append(row)

except:
    sys.exit()

if len(leagues) > 0:

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

    teams = add_teams(driver, conn, cursor, leagues)

    sqlQuery = "UPDATE transfers SET teamid = %s WHERE id = %s;"

    for team in teams:
        xmlUrl = 'http://www.managerzone.com/xml/team_playerlist.php?sport_id=1&team_id=' + str(team)
        driver.get(xmlUrl)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        soupText = soup.text

        soupText = soupText.replace('<Player id="', 'zz__mark1') 
        soupText = soupText.replace('" name="', 'zz__mark2') 
        
        playerIds = re.findall(r"zz__mark1(.*?)zz__mark2", soupText) 

        for playerId in playerIds:
            playerIdNum = int(playerId)
            values = (team, playerIdNum, )
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

