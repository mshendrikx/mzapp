from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

import pytz
import re
import time
import json
import mzcommon as mzc
import mzdeclaration as mzd

def get_searches(cursor):

    search = []
    searches = []
    countries = mzc.get_countries(cursor)

    for countryRow in countries:
        countryID = str(countryRow[0])
        ageCountry = countryRow[2]
        ageCount = 19
        while ageCount <= ageCountry:
            age_min_str = str(ageCount)
            if ageCount < ageCountry:
                age_max_str = age_min_str
            else:
                age_max_str = '37'
            search.append(countryID)
            search.append(age_min_str)
            search.append(age_max_str)
            search.append(countryRow[1])
            searches.append(search)
            search = []
            
            ageCount += 1
        
    return searches

def get_special_data(driver, playerTransfer):
    
    if playerTransfer.trainingdata == 'Y':
        try:
            link = 'https://www.managerzone.com/ajax.php?p=trainingGraph&sub=getJsonTrainingHistory&sport=soccer&player_id=' + str(playerTransfer.id)
            driver.get(link)
            playerTraining = driver.find_element(By.TAG_NAME, 'body')
            playerTraining = playerTraining.text[13:].split('{"showInNavigator":"true",')[0] 
            if len(playerTraining) > 1:
                playerTraining = playerTraining[0:-1] + ']'
            else:
                playerTraining += ']'
        except:
            logMessage = 'Fail to extract trainind data, player: ' + str(playerTransfer.id)
            mzc.write_log(logMessage, 'E')
            playerTransfer.trainingdata = 'N'
        try:
            trainingData = json.loads(playerTraining)
        except:
            logMessage = 'Fail to load json trainind data, player: ' + str(playerTransfer.id)
            mzc.write_log(logMessage, 'E')
            playerTransfer.trainingdata = 'N'

        if playerTransfer.trainingdata == 'Y':
            maxedHabs = []
            for graphData in trainingData:
                try:
                    if graphData['color'] == 'rgba(255,0,0,0.7)' and graphData['type'] == 'line':
                        maxData = graphData.get('data')[0]
                        maxedHabs.append(maxData.get('y'))
                except:
                    continue 

            if 1 in maxedHabs:
                playerTransfer.speedmax = 'Y'
            else:
                playerTransfer.speedmax = 'N'
            if 2 in maxedHabs:
                playerTransfer.staminamax = 'Y'
            else:
                playerTransfer.staminamax = 'N'
            if 3 in maxedHabs:
                playerTransfer.intelligencemax = 'Y'
            else:
                playerTransfer.intelligencemax = 'N'
            if 4 in maxedHabs: 
                playerTransfer.passingmax = 'Y'
            else:
                playerTransfer.passingmax = 'N'
            if 5 in maxedHabs: 
                playerTransfer.shootingmax = 'Y' 
            else:
                playerTransfer.shootingmax = 'N' 
            if 6 in maxedHabs:
                playerTransfer.headingmax = 'Y' 
            else:
                playerTransfer.headingmax = 'N' 
            if 7 in maxedHabs:
                playerTransfer.keepingmax = 'Y' 
            else:
                playerTransfer.keepingmax = 'N' 
            if 8 in maxedHabs:
                playerTransfer.controlmax = 'Y' 
            else:
                playerTransfer.controlmax = 'N' 
            if 9 in maxedHabs:
                playerTransfer.tacklingmax = 'Y'
            else:
                playerTransfer.tacklingmax = 'N'
            if 10 in maxedHabs: 
                playerTransfer.aerialmax = 'Y' 
            else:
                playerTransfer.aerialmax = 'N' 
            if 11 in maxedHabs:
                playerTransfer.playsmax = 'Y' 
            else:
                playerTransfer.playsmax = 'N' 

    if playerTransfer.scoutdata == 'Y':
        highAtt = []
        lowAtt = []
        try:
            link = 'https://www.managerzone.com/ajax.php?p=players&sub=scout_report&sport=soccer&pid=' + str(playerTransfer.id)
            driver.get(link)
            highAtt.append(driver.find_element(By.XPATH, '/html/body/div/div[2]/dl/dd[1]/div/div[2]/ul/li[2]/span').text)
            highAtt.append(driver.find_element(By.XPATH, '/html/body/div/div[2]/dl/dd[1]/div/div[2]/ul/li[3]/span').text)
            lowAtt.append(driver.find_element(By.XPATH, '/html/body/div/div[2]/dl/dd[2]/div/div[2]/ul/li[2]/span').text)
            lowAtt.append(driver.find_element(By.XPATH, '/html/body/div/div[2]/dl/dd[2]/div/div[2]/ul/li[3]/span').text)
            scoutStars = driver.find_elements(By.CLASS_NAME, 'stars')
            starCount = 1
            for scoutStar in scoutStars:
                stars = scoutStar.find_elements(By.TAG_NAME, 'i')
                for star in stars:
                    if star.get_attribute('class') == 'fa fa-star fa-2x lit':
                        if starCount == 1:
                            playerTransfer.starhigh += 1
                        elif starCount == 2:
                            playerTransfer.starlow += 1
                        else:
                            playerTransfer.startraining += 1
                    else:
                        continue
                starCount += 1
            attValue = 'H'
            if 'Speed' in highAtt:
                playerTransfer.speedscout = attValue
            if 'Stamina' in highAtt:
                playerTransfer.staminascout = attValue
            if 'Play Intelligence' in highAtt:
                playerTransfer.intelligencescout = attValue
            if 'Passing' in highAtt:
                playerTransfer.passingscout = attValue
            if 'Shooting' in highAtt:
                playerTransfer.shootingscout = attValue
            if 'Heading' in highAtt:
                playerTransfer.headingscout = attValue
            if 'Keeping' in highAtt:
                playerTransfer.keepingscout = attValue
            if 'Ball Control' in highAtt:
                playerTransfer.controlscout = attValue
            if 'Tackling' in highAtt:
                playerTransfer.tacklingscout = attValue
            if 'Aerial Passing' in highAtt:
                playerTransfer.aerialscout = attValue
            if 'Set Plays' in highAtt:
                playerTransfer.playsscout = attValue
            attValue = 'L'
            if 'Speed' in lowAtt:
                playerTransfer.speedscout = attValue
            if 'Stamina' in lowAtt:
                playerTransfer.staminascout = attValue
            if 'Play Intelligence' in lowAtt:
                playerTransfer.intelligencescout = attValue
            if 'Passing' in lowAtt:
                playerTransfer.passingscout = attValue
            if 'Shooting' in lowAtt:
                playerTransfer.shootingscout = attValue
            if 'Heading' in lowAtt:
                playerTransfer.headingscout = attValue
            if 'Keeping' in lowAtt:
                playerTransfer.keepingscout = attValue
            if 'Ball Control' in lowAtt:
                playerTransfer.controlscout = attValue
            if 'Tackling' in lowAtt:
                playerTransfer.tacklingscout = attValue
            if 'Aerial Passing' in lowAtt:
                playerTransfer.aerialscout = attValue
            if 'Set Plays' in lowAtt:
                playerTransfer.playsscout = attValue
            
        except:
            playerTransfer.scoutdata = 'N'

    return playerTransfer

def get_xpath_value(driver, isInt, posXpath, playerPos):

    xpath = '//*[@id="' + playerPos + '"]' + posXpath
    attValue = driver.find_element(By.XPATH, xpath).text
    if isInt == 'X':
        attValue = int(mzc.only_numerics(attValue))

    return attValue

def wait_players_container(driver):

    found = False
    count = 0
    while found == False:
        time.sleep(1)
        count += 1        
        try:
            element = driver.find_element(By.ID, 'thePlayers_0')
            found = True
        except:
            element = driver.find_element(By.ID, 'players_container')
            if element.text == 'No players found':
                found = True
        if count > 10:
            found = False
            break
    
    if element.text == 'No players found':
        found = False

    return found

def save_player(conn, cursor, playerTransf):

    try:
        cursor.execute("""
        REPLACE INTO transfers (
        id,
        name,
        country,
        onmarket,
        trainingdata,
        transferhistory,
        scoutdata,
        age,    
        season,
        totalskill,
        height,
        weight,
        foot,
        starhigh,
        starlow,
        startraining,
        value,
        salary,
        deadline,
        askingprice,
        latestbid,
        actualprice,
        speed,
        stamina,
        intelligence,
        passing,
        shooting,
        heading,
        keeping,
        control,
        tackling,
        aerial,
        plays,
        experience,
        form,
        speedscout,
        staminascout,
        intelligencescout,
        passingscout,
        shootingscout,
        headingscout,
        keepingscout,
        controlscout,
        tacklingscout,
        aerialscout,
        playsscout,
        speedmax,
        staminamax,
        intelligencemax,
        passingmax,
        shootingmax,
        headingmax,
        keepingmax,
        controlmax,
        tacklingmax,
        aerialmax,
        playsmax,
        retire,
        transferage)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            playerTransf.id, 
            playerTransf.name,
            playerTransf.country,
            playerTransf.onmarket,
            playerTransf.transferhistory,
            playerTransf.trainingdata,
            playerTransf.scoutdata,
            playerTransf.age,
            playerTransf.season,
            playerTransf.totalskill,
            playerTransf.height,
            playerTransf.weight,
            playerTransf.foot,
            playerTransf.starhigh,
            playerTransf.starlow,
            playerTransf.startraining,
            playerTransf.value, 
            playerTransf.salary,
            playerTransf.deadline,
            playerTransf.askingprice,
            playerTransf.latestbid,
            playerTransf.actualprice,
            playerTransf.speed,
            playerTransf.stamina,
            playerTransf.intelligence,
            playerTransf.passing,
            playerTransf.shooting,
            playerTransf.heading,
            playerTransf.keeping,
            playerTransf.control,
            playerTransf.tackling,
            playerTransf.aerial,
            playerTransf.plays,
            playerTransf.experience,
            playerTransf.form,
            playerTransf.speedscout,
            playerTransf.staminascout,
            playerTransf.intelligencescout,
            playerTransf.passingscout,
            playerTransf.shootingscout,
            playerTransf.headingscout,
            playerTransf.keepingscout,
            playerTransf.controlscout,
            playerTransf.tacklingscout,
            playerTransf.aerialscout,
            playerTransf.playsscout,
            playerTransf.speedmax,
            playerTransf.staminamax,
            playerTransf.intelligencemax,
            playerTransf.passingmax,
            playerTransf.shootingmax,
            playerTransf.headingmax,
            playerTransf.keepingmax,
            playerTransf.controlmax,
            playerTransf.tacklingmax,
            playerTransf.aerialmax,
            playerTransf.playsmax,
            playerTransf.retire,
            playerTransf.transferage))

        conn.commit()
        
    except:
        logMessage = 'Fail to update player data. Player: ' + str(playerTransf.id)
        mzc.write_log(logMessage, 'E')       

    conn.commit()

def update_transfers(driver, url, countryID, updatedIds):

    offset = 0
    totalHits = 0
    conn, cursor = mzc.db_connect()
    totalPlayers = 0
    while offset <= totalHits:
        localUrl = url + '&o=' + str(offset)
        driver.get(localUrl)
        bodyText = driver.page_source
        if totalHits == 0:
            try:
                reGroups = re.search('"totalHits":"(.*)","', bodyText[0:100])
                totalHits = int(reGroups.group(1))    
                if totalHits == 0:
                    break
            except Exception as e:
                logMessage = "Can´t find totalHits"
                mzc.write_log(logMessage, 'E')
                break
        playersText = bodyText.split('{') 
        playersText = playersText[1].split('thePlayers_') 
        del playersText[0]
        for playerText in playersText:
            try:
                auxText = playerText.replace('<span id="\\&quot;player_id_', 'aa_p_id')
                auxText = auxText.replace('\\&quot;"', 'zz_p_id')  
                foundId = re.findall(r"aa_p_id(.*?)zz_p_id", auxText)
                playerId = int(''.join(i for i in foundId[0] if i.isdigit()))
                if playerId in updatedIds:
                    continue
                playerData = mzd.PlayerTransf()
                playerData.id = playerId
                playerData.country = int(countryID)
                playerData.onmarket = 'X'
                auxText = playerText.replace('player_name\\&quot;">', 'aa_p_id')
                auxText = auxText.replace('&lt;', 'zz_p_id')  
                foundName = re.findall(r"aa_p_id(.*?)zz_p_id", auxText)
                playerData.name = foundName[0]
                auxText = playerText.replace('Age:&lt;\\/td&gt', 'aa_p_id')
                auxText = auxText.replace('&lt;', 'zz_p_id')  
                foundAge = re.findall(r"aa_p_id(.*?)zz_p_id", auxText)
                playerData.age = int(''.join(i for i in foundAge[0] if i.isdigit()))     
                playerData.transferage = playerData.age
                auxText = playerText.replace('Total Skill Balls:&lt;', 'aa_p_id')
                auxText = auxText.replace('&lt;', 'zz_p_id')  
                foundTtSkills = re.findall(r"aa_p_id(.*?)zz_p_id", auxText)
                playerData.totalskill = int(''.join(i for i in foundTtSkills[0] if i.isdigit()))
                auxText = playerText.replace('Height:&lt;', 'aa_p_id')
                auxText = auxText.replace(' cm&lt;', 'zz_p_id')  
                foundHeight = re.findall(r"aa_p_id(.*?)zz_p_id", auxText) 
                playerData.height = int(''.join(i for i in foundHeight[0] if i.isdigit()))        
                auxText = playerText.replace('Weight:&lt;', 'aa_p_id')
                auxText = auxText.replace(' kg&lt;', 'zz_p_id')  
                foundWeight = re.findall(r"aa_p_id(.*?)zz_p_id", auxText)         
                playerData.weight = int(''.join(i for i in foundWeight[0] if i.isdigit()))
                auxText = playerText.replace('Foot:&lt;', 'aa_p_id')
                auxText = auxText.replace('&lt;', 'zz_p_id')  
                foundFoot = re.findall(r"aa_p_id(.*?)zz_p_id", auxText)
                if 'Left' in foundFoot[0]:
                    playerData.foot = 'Left'
                elif 'Both' in foundFoot[0]:
                    playerData.foot = 'Both'
                else: 
                    playerData.foot = 'Right'            
                auxText = playerText.replace('Value:&lt;', 'aa_p_id')
                auxText = auxText.replace('R$', 'zz_p_id')  
                foundValue = re.findall(r"aa_p_id(.*?)zz_p_id", auxText)
                foundValue = foundValue[0].split('bold')[1]
                playerData.value = int(''.join(i for i in foundValue if i.isdigit()))
                auxText = playerText.replace('Salary:', 'aa_p_id')
                auxText = auxText.replace('R$', 'zz_p_id')  
                foundSalary = re.findall(r"aa_p_id(.*?)zz_p_id", auxText)
                foundSalary = foundSalary[0].split('bold')[1]
                playerData.salary = int(''.join(i for i in foundSalary if i.isdigit()))
                auxText = playerText.replace('Deadline&lt;', 'aa_p_id')
                auxText = auxText.replace('&lt;', 'zz_p_id')  
                foundDeadline = re.findall(r"aa_p_id(.*?)zz_p_id", auxText)
                auxDeadline = foundDeadline[0].split('<strong>')[1]    
                auxDeadline = auxDeadline.replace('\\/', '-')
                auxDeadline = datetime.strptime(auxDeadline, '%d-%m-%Y %I:%M%p') 
                playerData.deadline = int(auxDeadline.strftime('%Y%m%d%H%M'))
                auxText = playerText.replace('Asking Price&lt;', 'aa_p_id')
                auxText = auxText.replace('R$', 'zz_p_id')  
                foundAskingPrice = re.findall(r"aa_p_id(.*?)zz_p_id", auxText)  
                foundAskingPrice = foundAskingPrice[0].split('<strong>')[1]
                playerData.askingprice = int(''.join(i for i in foundAskingPrice if i.isdigit()))
                auxText = playerText.replace('Latest Bid:&lt;', 'aa_p_id')
                auxText = auxText.replace('R$', 'zz_p_id')  
                foundLatestBid = re.findall(r"aa_p_id(.*?)zz_p_id", auxText)  
                foundLatestBid = foundLatestBid[0].split('<strong>')[1]
                playerData.latestbid = int(''.join(i for i in foundLatestBid if i.isdigit()))
                if playerData.askingprice > playerData.latestbid:
                    playerData.actualprice = playerData.askingprice
                else:
                    playerData.actualprice = playerData.latestbid
                auxText = playerText.replace('Speed:" ', 'aa_p_id')
                auxText = auxText.replace('\\', 'zz_p_id')  
                foundSpeed = re.findall(r"aa_p_id(.*?)zz_p_id", auxText) 
                playerData.speed = int(foundSpeed[0])
                auxText = playerText.replace('Stamina:" ', 'aa_p_id')
                auxText = auxText.replace('\\', 'zz_p_id')  
                foundStamina = re.findall(r"aa_p_id(.*?)zz_p_id", auxText)  
                playerData.stamina = int(foundStamina[0])
                auxText = playerText.replace('Play" intelligence:="" ', 'aa_p_id')
                auxText = auxText.replace('\\', 'zz_p_id')  
                foundIntel = re.findall(r"aa_p_id(.*?)zz_p_id", auxText)   
                playerData.intelligence = int(foundIntel[0])
                auxText = playerText.replace('Passing:" ', 'aa_p_id')
                auxText = auxText.replace('\\', 'zz_p_id')  
                foundPassing = re.findall(r"aa_p_id(.*?)zz_p_id", auxText)  
                playerData.passing = int(foundPassing[0]) 
                auxText = playerText.replace('Shooting:" ', 'aa_p_id')
                auxText = auxText.replace('\\', 'zz_p_id')  
                foundShooting = re.findall(r"aa_p_id(.*?)zz_p_id", auxText)
                playerData.shooting = int(foundShooting[0])
                auxText = playerText.replace('Heading:" ', 'aa_p_id')
                auxText = auxText.replace('\\', 'zz_p_id')  
                foundHeading = re.findall(r"aa_p_id(.*?)zz_p_id", auxText)
                playerData.heading = int(foundHeading[0])
                auxText = playerText.replace('Keeping:" ', 'aa_p_id')
                auxText = auxText.replace('\\', 'zz_p_id')  
                foundKeeping = re.findall(r"aa_p_id(.*?)zz_p_id", auxText)
                playerData.keeping = int(foundKeeping[0])
                auxText = playerText.replace('Ball" control:="" ', 'aa_p_id')
                auxText = auxText.replace('\\', 'zz_p_id')  
                foundControl = re.findall(r"aa_p_id(.*?)zz_p_id", auxText)
                playerData.control = int(foundControl[0])
                auxText = playerText.replace('Tackling:" ', 'aa_p_id')
                auxText = auxText.replace('\\', 'zz_p_id')  
                foundTackling = re.findall(r"aa_p_id(.*?)zz_p_id", auxText)
                playerData.tackling = int(foundTackling[0])
                auxText = playerText.replace('Aerial" passing:="" ', 'aa_p_id')
                auxText = auxText.replace('\\', 'zz_p_id')  
                foundAerial = re.findall(r"aa_p_id(.*?)zz_p_id", auxText)
                playerData.aerial = int(foundAerial[0])
                auxText = playerText.replace('Set" plays:="" ', 'aa_p_id')
                auxText = auxText.replace('\\', 'zz_p_id')  
                foundPlays = re.findall(r"aa_p_id(.*?)zz_p_id", auxText)
                playerData.plays = int(foundPlays[0])
                auxText = playerText.replace('Experience:" ', 'aa_p_id')
                auxText = auxText.replace('\\', 'zz_p_id')  
                foundExperience = re.findall(r"aa_p_id(.*?)zz_p_id", auxText)
                playerData.experience = int(foundExperience[0])
                auxText = playerText.replace('Form:" ', 'aa_p_id')
                auxText = auxText.replace('\\', 'zz_p_id')  
                foundForm = re.findall(r"aa_p_id(.*?)zz_p_id", auxText)
                playerData.form = int(foundForm[0])
                auxText = playerText.replace('<strong>Season', 'aa_p_id')
                auxText = auxText.replace('&lt;\\/strong', 'zz_p_id')  
                foundSeason = re.findall(r"aa_p_id(.*?)zz_p_id", auxText) 
                playerData.season = int(foundSeason[0]) 
                if 'scout_report' in playerText:
                    playerData.scoutdata = 'Y'  
                else:
                    playerData.scoutdata = 'N'
                if 'training_graphs=' in playerText:
                    playerData.trainingdata = 'Y'
                else:
                    playerData.trainingdata = 'N'  
                if 'will retire' in playerText:
                    playerData.retire = 'Yes'
                else:
                    playerData.retire = 'No'
            except:
                logMessage = 'Fail to get basic data. Player: ' + str(playerData.id)
                mzc.write_log(logMessage, 'E')
                del playerData 
                continue

            try: 
                playerData = get_special_data(driver, playerData)
            except:
                logMessage = 'Fail to get special data. Player: ' + str(playerData.id)
                mzc.write_log(logMessage, 'E')

            try:               
                save_player(conn, cursor, playerData)
            except:
                logMessage = 'Fail to save data to DB. Player: ' + str(playerData.id)
                mzc.write_log(logMessage, 'E')

            totalPlayers += 1
            del playerData            

        offset += 20

    conn.close()

    return totalPlayers

def get_search_url(search):
    url = 'https://www.managerzone.com/ajax.php?p=transfer&sub=transfer-search&sport=soccer&issearch=true&u=&deadline=3&nationality=' + str(search[0])
    url = url + '&agea=' + str(search[1])
    url = url + '&ageb=' + str(search[2])
    return url

def updated_players():

    transfersId = []
    try:
        mzTimeZone =  mzd.MZ_TZ
        nowUtc = datetime.utcnow()
        nowUtc = nowUtc.replace(tzinfo=pytz.utc)
        nowBr = nowUtc.astimezone(pytz.timezone(mzTimeZone))
        nowBrStr = int(nowBr.strftime('%Y%m%d%H%M'))
        
        conn, cursor = mzc.db_connect()
        sqlQuery = 'SELECT id FROM transfers WHERE deadline > %s ;'
        values = (nowBrStr, )
        cursor.execute(sqlQuery, values)
       
        for row in cursor.fetchall():
            transfersId.append(row[0])

        conn.close()

    except:
        1 == 1

    return transfersId


