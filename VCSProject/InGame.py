import asyncio
import logging
import json
import threading
import requests
from IGTimer import VCSTimer     

class VCSIngame:
    def __init__(self):
        with open("config.json") as config_file:
            self._config = json.load(config_file)
        self.load_config()
        self.Timer = VCSTimer()
        self.event = None
        self.json = ""
        self.setData()

    def setData(self):
        self.BlueBar = {
            "Kill": 0,
            "Gold": "2.5k",
            "Turret": 0
        }
        self.RedBar = {
            "Kill": 0,
            "Gold": "2.5k",
            "Turret": 0
        }      
        self.NumDragonBlue = 1
        self.NumDragonRed = 1
        self.BlueDragon = {
            "dragon1": self.dragonpath + "None.png",
            "dragon2": self.dragonpath + "None.png",
            "dragon3": self.dragonpath + "None.png",
            "dragon4": self.dragonpath + "None.png",
        }
        self.RedDragon = {
            "dragon1": self.dragonpath + "None.png",
            "dragon2": self.dragonpath + "None.png",
            "dragon3": self.dragonpath + "None.png",
            "dragon4": self.dragonpath + "None.png",
        }


    def load_config(self):
        self.ip = self._config["OBS_IP"]
        vmip = self._config["Vmix_IP"]
        vmport = self._config["Vmix_Port"]
        self.Url = "http://" + vmip + ":" + vmport + "/api/?Function="
        self.port = self._config["Ingame_Event_Port"]
        self.dragonpath = self._config["Dragon_Icon"]

    def start(self):
        while True:
            try:
                 asyncio.run(self.process())
            except:
                pass

    async def process(self):
        self.reader, self.writer = await asyncio.open_connection(self.ip, self.port)
        try:
            while not self.reader.at_eof():
                data = await self.reader.readline()
                self.parseData(data)
        finally:
            self.writer.close()

    def parseData(self, data):
        if (data==b'}\n'):
            self.json += data.decode("utf-8")
            self.parseJSON()
            self.json = ""
        else:
            self.json += data.decode("utf-8")

    def parseJSON(self):
        try:
            self.event = json.loads(self.json)
        except:
            self.event = None
            return
        if (self.event["eventname"] == "OnGameStart"):
            self.setData()
        if (self.event["eventname"] == "OnChampionKill"):
            if (self.event["sourceTeam"] == "Order"):
                self.BlueBar["Kill"] += 1
            elif (self.event["sourceTeam"] == "Chaos"):
                self.RedBar["Kill"] += 1        
        if (self.event["eventname"] == "OnTurretDie"):
            if (self.event["sourceTeam"] == "Order"):
                self.RedBar["Turret"] += 1
            elif (self.event["sourceTeam"] == "Chaos"):
                self.BlueBar["Turret"] += 1        
        
        if (self.event["eventname"] == "OnKillDragon_Spectator"):
            if (self.event["sourceTeam"] == "Order"):
                if (self.event["other"] == "SRU_Dragon_Air6.1.1"):
                    self.BlueDragon["dragon"+str(self.NumDragonBlue)] = self.dragonpath + "Air.png"
                if (self.event["other"] == "SRU_Dragon_Fire6.2.1"):
                    self.BlueDragon["dragon"+str(self.NumDragonBlue)] = self.dragonpath + "Fire.png"
                if (self.event["other"] == "SRU_Dragon_Water6.3.1"):
                    self.BlueDragon["dragon"+str(self.NumDragonBlue)] = self.dragonpath + "Water.png"
                if (self.event["other"] == "SRU_Dragon_Earth6.4.1"):
                    self.BlueDragon["dragon"+str(self.NumDragonBlue)] = self.dragonpath + "Earth.png"
                self.NumDragonBlue += 1
            elif (self.event["sourceTeam"] == "Chaos"):
                if (self.event["other"] == "SRU_Dragon_Air6.1.1"):
                    self.RedDragon["dragon"+str(self.NumDragonRed)] = self.dragonpath + "Air.png"
                if (self.event["other"] == "SRU_Dragon_Fire6.2.1"):
                    self.RedDragon["dragon"+str(self.NumDragonRed)] = self.dragonpath + "Fire.png"
                if (self.event["other"] == "SRU_Dragon_Water6.3.1"):
                    self.RedDragon["dragon"+str(self.NumDragonRed)] = self.dragonpath + "Water.png"
                if (self.event["other"] == "SRU_Dragon_Earth6.4.1"):
                    self.RedDragon["dragon"+str(self.NumDragonRed)] = self.dragonpath + "Earth.png"
                self.NumDragonRed += 1