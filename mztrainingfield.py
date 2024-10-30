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


# Start of Program    

logFile = mzc.open_log_file('mzbid')

mzc.write_log('Start Process', 'W' )

mzc.write_log('Get players for bid', 'W')

conn, cursor = mzc.db_connect()

sqlQuery = "SELECT * FROM squad WHERE age > 18 ORDER BY age DESC;"
cursor.execute(sqlQuery)
conn.commit()

playerTrainning = []
playersTrainning = []
players1 = []

intelligence = 0
passing = 0
stamina = 0
speed = 0
    
for player in cursor.fetchall():
    playerTrainning.append(player.id)
    playerTrainning.append(player.name)
    if player[52] == 'Y':
        playerTrainning.append('1_senior_rest')
    elif player[24] == 'N' and intelligence < 5:
        playerTrainning.append('4_senior_skillgameintelligence')
        intelligence += 1
    elif player[21] == 'N' and stamina < 5:
        playerTrainning.append('3_senior_attrstamina')   
        stamina += 1   
    elif player[18] == 'N' and speed < 5:
        playerTrainning.append('2_senior_attrspeed')
        speed += 1
    elif player[27] == 'N' and passing < 5:
         playerTrainning.append('5_senior_skillpassing')
         passing += 1
    else:
        players1.append(player)
  
        

playersBid = players_bid(conn, cursor)

if len(playersBid) == 0:

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

# Player Bid
mzc.write_log('Biding players', 'W')
transfers_bid(driver, conn, cursor)
mzc.write_log('Unlock mzbid', 'W')
db_bid_lock(0, conn, cursor)

conn.close()

mzc.write_log('End Process', 'W')
