import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

REQUEST_TIME_OUT = 60
LOG_LOCATION = str(Path(__file__).parent.absolute()) + '/logs/'
DB_LOCATION = str(Path(__file__).parent.absolute()) + '/db/'
HTML_LOCATION = str(Path(__file__).parent.absolute()) + '/html/'
MZ_TZ = 'America/Sao_Paulo'
LOG_FILE = ''

MZUSER = os.environ['MZUSER']
MZPASS = os.environ['MZPASS']
MZVDISPLAY = os.environ['MZVDISPLAY']
MZMESSAGE = os.environ['MZMESSAGE']
MZOPTION = os.environ['MZOPTION']
MZDBUSER = os.environ['MZDBUSER']
MZDBPASS = os.environ['MZDBPASS']
MZDBNAME = os.environ['MZDBNAME']
MZDBHOST = os.environ['MZDBHOST']
MZREGION = os.environ['MZREGION']

class PlayerTransf:
    id = 0 
    name = ''
    country = 0
    onmarket = ''
    transferhistory = ''
    trainingdata = ''
    scoutdata = ''
    age = 0
    season = 0
    totalskill = 0
    height = 0
    weight = 0
    foot = ''
    starhigh = 0
    starlow = 0
    startraining = 0
    value = 0
    salary = 0
    deadline = 0
    askingprice = 0
    latestbid = 0
    actualprice = 0
    speed = 0
    stamina = 0
    intelligence = 0
    passing = 0
    shooting = 0 
    heading = 0 
    keeping = 0 
    control = 0 
    tackling = 0 
    aerial = 0 
    plays = 0 
    experience = 0
    form = 0
    speedscout = ''
    staminascout = ''
    intelligencescout = ''
    passingscout = ''
    shootingscout = ''
    headingscout = ''
    keepingscout = ''
    controlscout = ''
    tacklingscout = ''
    aerialscout = ''
    playsscout = ''
    speedmax = 'U'
    staminamax = 'U'
    intelligencemax = 'U' 
    passingmax = 'U' 
    shootingmax = 'U' 
    headingmax = 'U' 
    keepingmax = 'U' 
    controlmax = 'U' 
    tacklingmax = 'U' 
    aerialmax = 'U' 
    playsmax = 'U' 
    retire = ''
    maxbid = 0
    teamid = 0
    national = ''
    transferage = 0
    

class PlayerData:

    id = 0
    number = 0
    name = ''
    country = 0
    trainingdata = ''
    scoutdata = ''
    age = 0
    season = 0
    totalskill = 0
    height = 0
    weight = 0
    foot = ''
    starhigh = 0
    starlow = 0
    startraining = 0
    value = 0
    salary = 0
    speed = 0
    speedmax = ''
    speedscout = ''
    stamina = 0
    staminamax = ''
    staminascout = ''
    intelligence = 0
    intelligencemax = ''
    intelligencescout = ''
    passing = 0
    passingmax = ''
    passingscout = ''
    shooting = 0
    shootingmax = ''
    shootingscout = ''
    heading = 0
    headingmax = ''
    headingscout = ''
    keeping = 0
    keepingmax = ''
    keepingscout = ''
    control = 0
    controlmax = ''
    controlscout = ''
    tackling = 0
    tacklingmax = ''
    tacklingscout = ''
    aerial = 0
    aerialmax = ''
    aerialscout = ''
    plays = 0
    playsmax = ''
    playsscout = ''
    experience = 0
    form = 0
    trainingcamp = ''