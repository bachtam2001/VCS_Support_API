import websocket
import requests
import json
import threading, time
import logging
import asyncio
from flask import Flask
from BanPick import VCSBanPick
from InGame import VCSIngame

app = Flask("__name__")
BanPick = VCSBanPick()
Ingame = VCSIngame()

let = threading.Thread(target=Ingame.start)
let.start() 
Ingame.Timer.crawlData()

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def index():
    return '''VCS Broadcast API <br>
    /Ban : Get Champion Ban <br>
    /Pick : Get Champion Pick <br>
    /Team : Get Team Name <br>
    /Player : Get Player Name <br>
    /State : Get State and Timer <br>
    '''

@app.route('/Ban')
def getBan():
    return json.dumps(BanPick.Ban);

@app.route('/Pick')
def getPick():
    return json.dumps(BanPick.Pick);

@app.route('/Team')
def getTeam():
    Team = []
    for data in BanPick.TeamName:
        Team.append({"Team":data})
    return json.dumps(Team)

@app.route('/Player')
def getPlayer():
    Player = []
    for data in BanPick.TeamPlayer:
        Player.append({"Player":data})
    return json.dumps(Player)

@app.route('/State')
def getState():
    if (BanPick.Timer<10):
        Timer = "0" + str(BanPick.Timer)
    else:
        Timer = str(BanPick.Timer)
    return json.dumps([{"State":BanPick.StateArrow,"Timer": Timer}])
    
@app.route('/Ingame')
def getIngame():
    Ingame.BlueBar["Gold"] = Ingame.Timer.gold["blue"]
    Ingame.RedBar["Gold"] = Ingame.Timer.gold["red"]
    data = []
    data.append(Ingame.BlueBar)
    data.append(Ingame.RedBar)
    return json.dumps(data)

@app.route('/Dragon')
def getDragon():
    data = []
    data.append(Ingame.BlueDragon)
    data.append(Ingame.RedDragon)
    return json.dumps(data)

@app.route('/Timer')
def getTime():
    data = [{
        "Time": Ingame.Timer.live,
        "Dragon": Ingame.Timer.dragon["timer"],
        "Dragon_Type" : Ingame.Timer.dragon["type"],
        "Baron" : Ingame.Timer.baron["timer"]
    }]
    return json.dumps(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port='3005', threaded=True)