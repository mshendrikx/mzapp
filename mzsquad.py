from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import mzcommon as mzc
import mzdeclaration as mzd
import sys
import time


def partial_skill_value(partialText):

    if partialText == "width: 2px;":
        partialValue = 0.25
    elif partialText == "width: 4px;":
        partialValue = 0.50
    elif partialText == "width: 6px;":
        partialValue = 0.75
    else:
        partialValue = 0

    return partialValue


def scout_data(driver, playerData):

    if playerData.scoutdata == "Y":
        highAtt = []
        lowAtt = []
        try:
            link = (
                "https://www.managerzone.com/ajax.php?p=players&sub=scout_report&sport=soccer&pid="
                + str(playerData.id)
            )
            driver.get(link)
            highAtt.append(
                driver.find_element(
                    By.XPATH, "/html/body/div/div[2]/dl/dd[1]/div/div[2]/ul/li[2]/span"
                ).text
            )
            highAtt.append(
                driver.find_element(
                    By.XPATH, "/html/body/div/div[2]/dl/dd[1]/div/div[2]/ul/li[3]/span"
                ).text
            )
            lowAtt.append(
                driver.find_element(
                    By.XPATH, "/html/body/div/div[2]/dl/dd[2]/div/div[2]/ul/li[2]/span"
                ).text
            )
            lowAtt.append(
                driver.find_element(
                    By.XPATH, "/html/body/div/div[2]/dl/dd[2]/div/div[2]/ul/li[3]/span"
                ).text
            )
            scoutStars = driver.find_elements(By.CLASS_NAME, "stars")
            starCount = 1
            for scoutStar in scoutStars:
                stars = scoutStar.find_elements(By.TAG_NAME, "i")
                for star in stars:
                    if star.get_attribute("class") == "fa fa-star fa-2x lit":
                        if starCount == 1:
                            playerData.starhigh += 1
                        elif starCount == 2:
                            playerData.starlow += 1
                        else:
                            playerData.startraining += 1
                    else:
                        continue
                starCount += 1
            attValue = "H"
            if "Speed" in highAtt:
                playerData.speedscout = attValue
            if "Stamina" in highAtt:
                playerData.staminascout = attValue
            if "Play Intelligence" in highAtt:
                playerData.intelligencescout = attValue
            if "Passing" in highAtt:
                playerData.passingscout = attValue
            if "Shooting" in highAtt:
                playerData.shootingscout = attValue
            if "Heading" in highAtt:
                playerData.headingscout = attValue
            if "Keeping" in highAtt:
                playerData.keepingscout = attValue
            if "Ball Control" in highAtt:
                playerData.controlscout = attValue
            if "Tackling" in highAtt:
                playerData.tacklingscout = attValue
            if "Aerial Passing" in highAtt:
                playerData.aerialscout = attValue
            if "Set Plays" in highAtt:
                playerData.playsscout = attValue
            attValue = "L"
            if "Speed" in lowAtt:
                playerData.speedscout = attValue
            if "Stamina" in lowAtt:
                playerData.staminascout = attValue
            if "Play Intelligence" in lowAtt:
                playerData.intelligencescout = attValue
            if "Passing" in lowAtt:
                playerData.passingscout = attValue
            if "Shooting" in lowAtt:
                playerData.shootingscout = attValue
            if "Heading" in lowAtt:
                playerData.headingscout = attValue
            if "Keeping" in lowAtt:
                playerData.keepingscout = attValue
            if "Ball Control" in lowAtt:
                playerData.controlscout = attValue
            if "Tackling" in lowAtt:
                playerData.tacklingscout = attValue
            if "Aerial Passing" in lowAtt:
                playerData.aerialscout = attValue
            if "Set Plays" in lowAtt:
                playerData.playsscout = attValue

        except:
            playerData.scoutdata = "N"

    return playerData


def squad_data(driver):

    driver.get("https://www.managerzone.com/?p=players")

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "players_container"))
    )

    playersContainer = driver.find_elements(By.CLASS_NAME, "playerContainer")

    playersData = []

    for playerContainer in playersContainer:
        containerId = playerContainer.get_attribute("id")
        preXPath = '//*[@id="' + containerId + '"]'
        playerData = mzd.PlayerData()
        playerData.id = int(
            playerContainer.find_element(By.CLASS_NAME, "player_id_span").text
        )
        playerData.number = int(
            playerContainer.find_element(By.CLASS_NAME, "subheader").text.split(".")[0]
        )
        playerData.name = playerContainer.find_element(
            By.CLASS_NAME, "player_name"
        ).text
        playerData.country = 0
        playerData.trainingdata = "Y"
        try:
            playerContainer.find_element(
                By.CSS_SELECTOR, "span.player_icon_placeholder.scout_report.font-based"
            )
            playerData.scoutdata = "Y"
        except:
            playerData.scoutdata = "N"
        playerData.age = int(
            mzc.only_numerics(
                playerContainer.find_element(
                    By.XPATH,
                    preXPath + "/div/div/div[1]/table[1]/tbody/tr[1]/td[1]/strong",
                ).text
            )
        )
        playerData.season = int(
            mzc.only_numerics(
                playerContainer.find_element(
                    By.XPATH,
                    preXPath + "/div/div/div[1]/table[1]/tbody/tr[3]/td/strong",
                ).text
            )
        )
        playerData.height = int(
            mzc.only_numerics(
                playerContainer.find_element(
                    By.XPATH,
                    preXPath + "/div/div/div[1]/table[1]/tbody/tr[2]/td[1]/strong",
                ).text
            )
        )
        playerData.weight = int(
            mzc.only_numerics(
                playerContainer.find_element(
                    By.XPATH,
                    preXPath + "/div/div/div[1]/table[1]/tbody/tr[2]/td[2]/strong",
                ).text
            )
        )
        playerData.foot = playerContainer.find_element(
            By.XPATH, preXPath + "/div/div/div[1]/table[1]/tbody/tr[1]/td[2]/strong"
        ).text
        playerData.starhigh = 0
        playerData.starlow = 0
        playerData.startraining = 0

        if playerData.age < 19:
            playerData.value = int(
                mzc.only_numerics(
                    playerContainer.find_element(
                        By.XPATH,
                        preXPath + "/div/div/div[1]/table[1]/tbody/tr[5]/td/span",
                    ).text
                )
            )
        else:
            try:
                playerData.value = int(
                    mzc.only_numerics(
                        playerContainer.find_element(
                            By.XPATH,
                            preXPath + "/div/div/div[1]/table[1]/tbody/tr[5]/td/span",
                        ).text
                    )
                )
                playerData.salary = int(
                    mzc.only_numerics(
                        playerContainer.find_element(
                            By.XPATH,
                            preXPath + "/div/div/div[1]/table[1]/tbody/tr[6]/td/span",
                        ).text
                    )
                )
            except:
                playerData.value = int(
                    mzc.only_numerics(
                        playerContainer.find_element(
                            By.XPATH,
                            preXPath + "/div/div/div[1]/table[1]/tbody/tr[6]/td/span",
                        ).text
                    )
                )
                playerData.salary = int(
                    mzc.only_numerics(
                        playerContainer.find_element(
                            By.XPATH,
                            preXPath + "/div/div/div[1]/table[1]/tbody/tr[7]/td/span",
                        ).text
                    )
                )

        playerData.speed = int(
            mzc.only_numerics(
                playerContainer.find_element(
                    By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[1]/td[6]/span"
                ).text
            )
        )
        playerData.speed += partial_skill_value(
            playerContainer.find_element(
                By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[1]/td[7]/div/div"
            ).get_attribute("style")
        )
        if (
            playerContainer.find_element(
                By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[1]/td[6]/span"
            ).get_attribute("class")
            == "maxed"
        ):
            playerData.speedmax = "Y"
        else:
            playerData.speedmax = "N"
        playerData.speedscout = ""

        playerData.stamina = int(
            mzc.only_numerics(
                playerContainer.find_element(
                    By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[2]/td[6]/span"
                ).text
            )
        )
        playerData.stamina += partial_skill_value(
            playerContainer.find_element(
                By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[2]/td[7]/div/div"
            ).get_attribute("style")
        )
        if (
            playerContainer.find_element(
                By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[2]/td[6]/span"
            ).get_attribute("class")
            == "maxed"
        ):
            playerData.staminamax = "Y"
        else:
            playerData.staminamax = "N"
        playerData.staminascout = ""

        playerData.intelligence = int(
            mzc.only_numerics(
                playerContainer.find_element(
                    By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[3]/td[6]/span"
                ).text
            )
        )
        playerData.intelligence += partial_skill_value(
            playerContainer.find_element(
                By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[3]/td[7]/div/div"
            ).get_attribute("style")
        )
        if (
            playerContainer.find_element(
                By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[3]/td[6]/span"
            ).get_attribute("class")
            == "maxed"
        ):
            playerData.intelligencemax = "Y"
        else:
            playerData.intelligencemax = "N"
        playerData.intelligencescout = ""

        playerData.passing = int(
            mzc.only_numerics(
                playerContainer.find_element(
                    By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[4]/td[6]/span"
                ).text
            )
        )
        playerData.passing += partial_skill_value(
            playerContainer.find_element(
                By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[4]/td[7]/div/div"
            ).get_attribute("style")
        )
        if (
            playerContainer.find_element(
                By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[4]/td[6]/span"
            ).get_attribute("class")
            == "maxed"
        ):
            playerData.passingmax = "Y"
        else:
            playerData.passingmax = "N"
        playerData.passingscout = ""

        playerData.shooting = int(
            mzc.only_numerics(
                playerContainer.find_element(
                    By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[5]/td[6]/span"
                ).text
            )
        )
        playerData.shooting += partial_skill_value(
            playerContainer.find_element(
                By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[5]/td[7]/div/div"
            ).get_attribute("style")
        )
        if (
            playerContainer.find_element(
                By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[5]/td[6]/span"
            ).get_attribute("class")
            == "maxed"
        ):
            playerData.shootingmax = "Y"
        else:
            playerData.shootingmax = "N"
        playerData.shootingscout = ""

        playerData.heading = int(
            mzc.only_numerics(
                playerContainer.find_element(
                    By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[6]/td[6]/span"
                ).text
            )
        )
        playerData.heading += partial_skill_value(
            playerContainer.find_element(
                By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[6]/td[7]/div/div"
            ).get_attribute("style")
        )
        if (
            playerContainer.find_element(
                By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[6]/td[6]/span"
            ).get_attribute("class")
            == "maxed"
        ):
            playerData.headingmax = "Y"
        else:
            playerData.headingmax = "N"
        playerData.headingscout = ""

        playerData.keeping = int(
            mzc.only_numerics(
                playerContainer.find_element(
                    By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[7]/td[6]/span"
                ).text
            )
        )
        playerData.keeping += partial_skill_value(
            playerContainer.find_element(
                By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[7]/td[7]/div/div"
            ).get_attribute("style")
        )
        if (
            playerContainer.find_element(
                By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[7]/td[6]/span"
            ).get_attribute("class")
            == "maxed"
        ):
            playerData.keepingmax = "Y"
        else:
            playerData.keepingmax = "N"
        playerData.keepingscout = ""

        playerData.control = int(
            mzc.only_numerics(
                playerContainer.find_element(
                    By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[8]/td[6]/span"
                ).text
            )
        )
        playerData.control += partial_skill_value(
            playerContainer.find_element(
                By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[8]/td[7]/div/div"
            ).get_attribute("style")
        )
        if (
            playerContainer.find_element(
                By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[8]/td[6]/span"
            ).get_attribute("class")
            == "maxed"
        ):
            playerData.controlmax = "Y"
        else:
            playerData.controlmax = "N"
        playerData.controlscout = ""

        playerData.tackling = int(
            mzc.only_numerics(
                playerContainer.find_element(
                    By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[9]/td[6]/span"
                ).text
            )
        )
        playerData.tackling += partial_skill_value(
            playerContainer.find_element(
                By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[9]/td[7]/div/div"
            ).get_attribute("style")
        )
        if (
            playerContainer.find_element(
                By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[9]/td[6]/span"
            ).get_attribute("class")
            == "maxed"
        ):
            playerData.tacklingmax = "Y"
        else:
            playerData.tacklingmax = "N"
        playerData.tacklingscout = ""

        playerData.aerial = int(
            mzc.only_numerics(
                playerContainer.find_element(
                    By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[10]/td[6]/span"
                ).text
            )
        )
        playerData.aerial += partial_skill_value(
            playerContainer.find_element(
                By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[10]/td[7]/div/div"
            ).get_attribute("style")
        )
        if (
            playerContainer.find_element(
                By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[10]/td[6]/span"
            ).get_attribute("class")
            == "maxed"
        ):
            playerData.aerialmax = "Y"
        else:
            playerData.aerialmax = "N"
        playerData.aerialscout = ""

        playerData.plays = int(
            mzc.only_numerics(
                playerContainer.find_element(
                    By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[11]/td[6]/span"
                ).text
            )
        )
        playerData.plays += partial_skill_value(
            playerContainer.find_element(
                By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[11]/td[7]/div/div"
            ).get_attribute("style")
        )
        if (
            playerContainer.find_element(
                By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[11]/td[6]/span"
            ).get_attribute("class")
            == "maxed"
        ):
            playerData.playsmax = "Y"
        else:
            playerData.playsmax = "N"
        playerData.playsscout = ""

        playerData.experience = int(
            mzc.only_numerics(
                playerContainer.find_element(
                    By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[12]/td[6]/span"
                ).text
            )
        )
        playerData.experience += partial_skill_value(
            playerContainer.find_element(
                By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[12]/td[7]/div/div"
            ).get_attribute("style")
        )

        playerData.form = int(
            mzc.only_numerics(
                playerContainer.find_element(
                    By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[13]/td[6]/span"
                ).text
            )
        )
        playerData.form += partial_skill_value(
            playerContainer.find_element(
                By.XPATH, preXPath + "/div/div/div[3]/table/tbody/tr[13]/td[7]/div/div"
            ).get_attribute("style")
        )

        playerData.totalskill = (
            playerData.speed
            + playerData.stamina
            + playerData.intelligence
            + playerData.passing
            + playerData.shooting
            + playerData.heading
            + playerData.keeping
            + playerData.control
            + playerData.tackling
            + playerData.aerial
            + playerData.plays
            + playerData.experience
        )

        try:
            playerContainer.find_element(By.CLASS_NAME, "training_camp_player")
            playerData.trainingcamp = "Y"
        except:
            playerData.trainingcamp = "N"

        playersData.append(playerData)

    for playerData in playersData:
        playerData = scout_data(driver, playerData)

    return playersData


def save_players(playersData):

    conn, cursor = mzc.db_connect()

    for playerData in playersData:

        try:
            cursor.execute(
                """
            REPLACE INTO squad (
            id,
            number,
            name,
            country,
            trainingdata,
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
            trainingcamp)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
                (
                    playerData.id,
                    playerData.number,
                    playerData.name,
                    playerData.country,
                    playerData.trainingdata,
                    playerData.scoutdata,
                    playerData.age,
                    playerData.season,
                    playerData.totalskill,
                    playerData.height,
                    playerData.weight,
                    playerData.foot,
                    playerData.starhigh,
                    playerData.starlow,
                    playerData.startraining,
                    playerData.value,
                    playerData.salary,
                    playerData.speed,
                    playerData.stamina,
                    playerData.intelligence,
                    playerData.passing,
                    playerData.shooting,
                    playerData.heading,
                    playerData.keeping,
                    playerData.control,
                    playerData.tackling,
                    playerData.aerial,
                    playerData.plays,
                    playerData.experience,
                    playerData.form,
                    playerData.speedscout,
                    playerData.staminascout,
                    playerData.intelligencescout,
                    playerData.passingscout,
                    playerData.shootingscout,
                    playerData.headingscout,
                    playerData.keepingscout,
                    playerData.controlscout,
                    playerData.tacklingscout,
                    playerData.aerialscout,
                    playerData.playsscout,
                    playerData.speedmax,
                    playerData.staminamax,
                    playerData.intelligencemax,
                    playerData.passingmax,
                    playerData.shootingmax,
                    playerData.headingmax,
                    playerData.keepingmax,
                    playerData.controlmax,
                    playerData.tacklingmax,
                    playerData.aerialmax,
                    playerData.playsmax,
                    playerData.trainingcamp,
                ),
            )

            conn.commit()

        except:
            logMessage = "Fail to update player data. Player: " + str(playerData.id)
            # mzc.write_log(logMessage, 'E')

        conn.commit()


# Start of Program
logFile = mzc.open_log_file("mzsquad")

mzc.write_log("Start Process", "W")

display = mzc.virtual_display()

mzc.write_log("Login Process", "W")

driverError = 99

loginCount = 0
while driverError > 0:

    driver, driverError = mzc.mz_login(mzd.MZUSER, mzd.MZPASS, True, True, False)
    if driverError == 0:
        mzc.write_log("Successful login into managerzone.com", "S")
    elif driverError == 1:
        mzc.write_log("Driver initlization fails", "E")
    elif driverError == 2:
        mzc.write_log("Missing login fields", "E")
    elif driverError == 3:
        mzc.write_log("Set cookies fails", "E")
    elif driverError == 4:
        mzc.write_log("Login button fails", "E")

    if driverError > 0:
        time.sleep(5)

    loginCount += 1

    if loginCount > 20:
        mzc.write_log("Cant login in magerzone.com", "E")
        sys.exit()

# Get Squad Data
mzc.write_log("Get Squad Data", "W")
squadData = squad_data(driver)
save_players(squadData)

driver.close()
driver.quit()

mzc.write_log("End Process", "W")
