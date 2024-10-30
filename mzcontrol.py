from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import mzcommon as mzc
import mzdeclaration as mzd
import sys
import time

def update_countries(driver, logFile):

    conn, cursor = mzc.db_connect()

    driver.get('https://www.managerzone.com/?p=national_teams&type=senior')
    selCountry = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, "cid")))
    countries_sel = selCountry.find_elements(By.TAG_NAME, 'option')

    country = []
    countries = []
    for country_sel in countries_sel:
        country.append(country_sel.get_attribute('value'))
        country.append(country_sel.text)
        countries.append(country)
        country = []
    
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
            mzc.write_log(msgLog, 'E')
            continue
        try:
            sql = ''' 
            UPDATE countries 
            SET name = %s, flag = %s
            WHERE id = %s
            ''' 
            values = (countryName, countryImage, countryID)

            cursor.execute(sql, values)
            
            conn.commit()

        except:
            1 == 1

        if cursor.rowcount < 1:
            try: 
                cursor.execute("""
                INSERT INTO countries (
                id,
                name,
                agetrans,
                flag,
                region)
                VALUES (%s,%s,%s,%s,%s)
                """,(
                    countryID,
                    countryName,
                    19,
                    countryImage,
                    ''))

                conn.commit()

            except:
                1 == 1

    conn.close()
    
def update_season(driver):

    conn, cursor = mzc.db_connect()

    driver.get('https://www.managerzone.com/?p=clubhouse')

    seasonInfo = WebDriverWait(driver, 30).until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="header-stats-wrapper"]/h5[3]')))

    season = int(mzc.only_numerics(seasonInfo.text.split('·')[0]))

    try:
        cursor.execute("SELECT * FROM mzctrl")
        conn.commit()
    except:
        mzc.write_log('No data in table mzctrl', 'I')

    if cursor.rowcount < 1:

        try:
            sqlExec = 'INSERT INTO mzctrl (id, season, deadline) VALUES (%s,%s,%s)'
            sqlValues = ('MZCTRL', 0, 0 )
            cursor.execute(sqlExec, sqlValues)
        except:
            mzc.write_log('SQL INSERT Error in table mzctrl', 'E')

        conn.commit()

    try:
        sql = ''' 
        UPDATE mzctrl 
        SET season = %s
        WHERE id = 'MZCTRL'
        ''' 
        values = (season,)    
        cursor.execute(sql, values)        
        conn.commit()
    except:
        1 == 1

    try:
        sql = 'UPDATE transfers SET age = %s - season;' 
        values = (season,)    
        cursor.execute(sql, values)        
        conn.commit()
    except:
        1 == 1        

    try:
        sql = "UPDATE transfers SET retire = 'Yes' WHERE age > 37;"
        cursor.execute(sql)        
        conn.commit()
    except:
        1 == 1     

# Start of Program    
logFile = mzc.open_log_file('mzcontrol')

mzc.write_log('Start Process', 'W' )

display = mzc.virtual_display()

mzc.write_log('Login Process', 'W')

driverError = 99

loginCount = 0
while driverError > 0:

    driver, driverError = mzc.mz_login(mzd.MZUSER, mzd.MZPASS, True, True, False)
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
        time.sleep(5)

    loginCount += 1

    if loginCount > 20:
        mzc.write_log('Cant login in magerzone.com', 'E')
        sys.exit()

# Update Season
mzc.write_log('Update Season', 'W')
update_season(driver)

# Update Countries
mzc.write_log('Update Countries', 'W')
update_countries(driver, logFile)

driver.close()
driver.quit()

mzc.write_log('End Process', 'W')
