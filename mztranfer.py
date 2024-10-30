from datetime import datetime
import pytz
import sys
import time
import mzdeclaration as mzd
import mzcommon as mzc
import mztransdef as mztd
import os

playerList = []
playerCount = 0

mzTimeZone = 'America/Sao_Paulo'
nowUtc = datetime.utcnow()
nowUtc = nowUtc.replace(tzinfo=pytz.utc)
nowBr = nowUtc.astimezone(pytz.timezone(mzTimeZone))
nowBrFile = nowBr.strftime('%Y%m%d%H%M')
newDeadline = int(nowBr.strftime('%Y%m%d%H%M'))

logFile = mzc.open_log_file('mztransfer')

mzc.write_log('Start Process', 'W')

#display = mzc.virtual_display()

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
        os.system('/home/ubuntu/apps/mznew/venv/bin/python3 /home/ubuntu/apps/mznew/mztranfer.py')
        sys.exit()

# Database cursor
mzc.write_log('Connect DB', 'W')
conn, cursor = mzc.db_connect()
if conn == None:
    mzc.write_log('DB connect fails. Exit', 'E')
    sys.exit()
else:
    mzc.write_log('DB connected', 'S')

# Get countries
mzc.write_log('Get Transfer Market Searches', 'W')
searches = mztd.get_searches(cursor)
conn.close()

if searches == []:
    mzc.write_log('No searches found. Exit', 'E')
    sys.exit()

# Get player basic data
mzc.write_log('Get player data', 'W')
playersList = []

totalPlayers = 0
searchPlayers = 0

updatedIds = mztd.updated_players()

for search in searches:
    searchUrl = mztd.get_search_url(search)
    searchPlayers = mztd.update_transfers(driver, searchUrl, search[0], updatedIds)
    totalPlayers += searchPlayers
    logRow = search[3] + ' age from ' + str(search[1]) + ' to ' + str(search[2]) + ' players: ' + str(searchPlayers)
    mzc.write_log(logRow, 'W')

logRow = 'Total players: ' + str(totalPlayers)
mzc.write_log(logRow, 'W')

# Time
mzTimeZone = 'America/Sao_Paulo'
nowUtc = datetime.utcnow()
nowUtc = nowUtc.replace(tzinfo=pytz.utc)
nowBr = nowUtc.astimezone(pytz.timezone(mzTimeZone))
nowBrStr = int(nowBr.strftime('%Y%m%d%H%M'))

# update onmarket flag
mzc.write_log('Update onmarket flag', 'W')

conn, cursor = mzc.db_connect()

cursor.execute('''
UPDATE transfers
   SET onmarket = ' '
 WHERE onmarket = 'X' 
   AND deadline < %s ;
''', (nowBrStr,))

conn.commit()

# Update new deadline
mzc.write_log('Update new deadline', 'W')
cursor.execute('''
UPDATE mzctrl
   SET deadline = %s
 WHERE id = 'MZCTRL' ;
''', (newDeadline,))

conn.commit()
conn.close()

# Backup database
mzc.write_log('Backup database', 'W')
mzc.db_backup()

driver.close()
driver.quit()

mzc.write_log('End Process', 'S')
