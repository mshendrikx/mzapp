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
import psutil

#mzd.MZMESSAGE = ''

def players_bid(conn, cursor):
    
    # Time
    nowUtc = datetime.utcnow()
    nowUtc = nowUtc.replace(tzinfo=pytz.utc)
    nowBr = nowUtc.astimezone(pytz.timezone(mzd.MZ_TZ))
    #nowBrStr = int(nowBr.strftime('%Y%m%d%H%M'))
    time_change = timedelta(minutes=20)
    maxDate = nowBr + time_change
    maxDateStr = int(maxDate.strftime('%Y%m%d%H%M'))

    sqlQuery = "SELECT * FROM transfers WHERE maxbid > 0;"
    cursor.execute(sqlQuery)
    conn.commit()

    playersData = []
    for row in cursor.fetchall():
        if row[18] > maxDateStr:
            continue
#        elif row[18] < nowBrStr:
#            sqlQuery = 'UPDATE transfers SET maxbid = 0 WHERE id = %s;' 
#            values = (row[0],) 
#            cursor.execute(sqlQuery, values) 
#            conn.commit()
#            continue
        playerData = mzd.PlayerTransf()
        playerData.id = row[0]
        playerData.name = row[1]
        playerData.country = row[2]
        playerData.onmarket = row[3]
        playerData.transferhistory = row[4]
        playerData.trainingdata = row[5]
        playerData.scoutdata = row[6]
        playerData.age = row[7]
        playerData.season = row[8]
        playerData.totalskill = row[9]
        playerData.height = row[10]
        playerData.weight = row[11]
        playerData.foot = row[12]
        playerData.starhigh = row[13]
        playerData.starlow = row[14]
        playerData.startraining = row[15]
        playerData.value = row[16]
        playerData.salary = row[17]
        playerData.deadline = row[18]
        playerData.askingprice = row[19]
        playerData.latestbid = row[20]
        playerData.actualprice = row[21]
        playerData.speed = row[22]
        playerData.stamina = row[25]
        playerData.intelligence = row[28]
        playerData.passing = row[31]
        playerData.shooting = row[34] 
        playerData.heading = row[37] 
        playerData.keeping = row[40] 
        playerData.control = row[43] 
        playerData.tackling = row[46] 
        playerData.aerial = row[49] 
        playerData.plays = row[52] 
        playerData.experience = row[55] 
        playerData.form = row[56] 
        playerData.speedscout = row[24] 
        playerData.staminascout = row[27] 
        playerData.intelligencescout = row[30] 
        playerData.passingscout = row[33] 
        playerData.shootingscout = row[36] 
        playerData.headingscout = row[39] 
        playerData.keepingscout = row[42] 
        playerData.controlscout = row[45] 
        playerData.tacklingscout = row[48] 
        playerData.aerialscout = row[51] 
        playerData.playsscout = row[54] 
        playerData.speedmax = row[23]
        playerData.staminamax = row[26]
        playerData.intelligencemax = row[29] 
        playerData.passingmax = row[32]
        playerData.shootingmax = row[35]
        playerData.headingmax = row[38]
        playerData.keepingmax = row[41]
        playerData.controlmax = row[44]
        playerData.tacklingmax = row[47]
        playerData.aerialmax = row[50]
        playerData.playsmax = row[53] 
        playerData.retire = row[57]
        playerData.maxbid = row[58]

        playersData.append(playerData)

    return playersData

def transfers_bid(driver, conn, cursor):

    execCtrl = True

    while execCtrl == True:
        playersData = players_bid(conn, cursor)
        if len(playersData) == 0:
            execCtrl = False
            continue

        for playerData in playersData:
            bidUrl = 'https://www.managerzone.com/?p=transfer&sub=players&u=' + str(playerData.id)
            try:
                driver.switch_to.default_content()
            except:
                1 == 1 
            try:
                driver.get(bidUrl)
                element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID, 'thePlayers_0')))
            except:
                sqlQuery = 'UPDATE transfers SET maxbid = 0 WHERE id = %s;' 
                values = (playerData.id,) 
                cursor.execute(sqlQuery, values) 
                conn.commit()
                continue
            try:
                latestBidEl = driver.find_element(By.XPATH, '//*[@id="thePlayers_0"]/div/div/div[2]/div/div[2]/table/tbody/tr/td[1]/table/tbody/tr[1]/td[2]')
                latestBid = int(mzc.only_numerics(latestBidEl.text))
                latestBidFor = int(mzc.only_numerics(latestBidEl.get_attribute("title")))
                askingPrice = int(mzc.only_numerics(driver.find_element(By.XPATH, '//*[@id="thePlayers_0"]/div/div/div[2]/div/div[1]/table/tbody/tr[4]/td[2]/strong').text))
                #aux = str(driver.find_element(By.XPATH, '//*[@id="thePlayers_0"]/div/div/div[2]/div/div[1]/table/tbody/tr[3]/td[2]/strong').text)
                #auxDeadline = datetime.strptime(aux, '%d/%m/%Y %I:%M%p')
                #newDeadline = int(auxDeadline.strftime('%Y%m%d%H%M'))
                if latestBid == 0:
                    if askingPrice > 0:
                        bidValue = askingPrice
                    else:
                        bidValue = 1                    
                else:
                    if latestBid > latestBidFor and latestBidFor > 0:
                        conValue = latestBid / latestBidFor
                        bidValue = math.ceil(latestBidFor * 1.05 * conValue)
                    else:
                        bidValue = math.ceil(latestBid * 1.05)
                #try:
                #    sqlQuery = 'UPDATE transfers SET deadline = %s WHERE id = %s;' 
                #    values = (newDeadline, playerData.id,) 
                #    cursor.execute(sqlQuery, values) 
                #    conn.commit()
                #except:
                #    1 == 1
            except:
                continue

            if bidValue > playerData.maxbid:
                try:
                    sqlQuery = 'UPDATE transfers SET maxbid = 0 WHERE id = %s;' 
                    values = (playerData.id,) 
                    cursor.execute(sqlQuery, values) 
                    conn.commit()
                    continue
                except:
                    continue

            try:
                buyButton = driver.find_element(By.XPATH, '//*[@id="thePlayers_0"]/div/div/div[2]/div/div[2]/table/tbody/tr/td[2]/span[1]/a')
                buyButton.click()
            except:
                continue
            
            try:
                bidButton = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "transfer_place_bid_button")))
            except:
                continue

            try:
                element = driver.find_element(By.ID, 'buyform_bid_user_currency') 
            except:
                try:
                    element = driver.find_element(By.ID, 'buyform_bid_player_currency') 
                except:
                    continue
            
            try:
                element.clear()
                element.send_keys(str(bidValue))
                bidButton = driver.find_element(By.ID, 'transfer_place_bid_button')
                bidButton.click()
                time.sleep(1)
                alert = driver.switch_to.alert
                alert.accept()
                driver.switch_to.default_content()
            except:
                continue
            try:
                sqlQuery = 'UPDATE transfers SET actualprice = %s WHERE id = %s;' 
                values = (bidValue, playerData.id,) 
                cursor.execute(sqlQuery, values) 
                conn.commit()
            except:
                1 == 1
            
        time.sleep(15)

def db_bid_lock(value, conn, cursor):

    sqlQuery = "UPDATE mzctrl SET bidctrl=%s WHERE id = 'MZCTRL';"
    values = (value, )
    cursor.execute(sqlQuery, values)
    conn.commit()

# Start of Program    

logFile = mzc.open_log_file('mzbid')

mzc.write_log('Start Process', 'W' )

mzc.write_log('Get players for bid', 'W')

conn, cursor = mzc.db_connect()

playersBid = players_bid(conn, cursor)

if len(playersBid) == 0:
    db_bid_lock(0, conn, cursor)
    mzc.write_log('No players for bid', 'S')
    mzc.write_log('End Process', 'W')
    sys.exit()

sqlQuery = "SELECT bidctrl FROM mzctrl WHERE id = 'MZCTRL';"
cursor.execute(sqlQuery)

bidBlock = int(cursor.fetchone()[0])

if bidBlock == 1:
    mzc.write_log('mzbid alredy in execution', 'W')
    mzc.write_log('End Process', 'W')
    sys.exit()
else:
    mzc.write_log('Lock mzbid', 'W')
    db_bid_lock(1, conn, cursor)

mzc.write_log('Login Process', 'W')

#mzd.MZVDISPLAY = False
#display = mzc.virtual_display()

driverError = 99
loginCount = 0
loginError = False
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
        driverError = 0
        loginError = True


if not loginError:
    # Player Bid
    mzc.write_log('Biding players', 'W')
    transfers_bid(driver, conn, cursor)
else:
    mzc.write_log('Fail to bid', 'E')
    
mzc.write_log('Unlock mzbid', 'W')
db_bid_lock(0, conn, cursor)

conn.close()

mzc.write_log('End Process', 'W')
