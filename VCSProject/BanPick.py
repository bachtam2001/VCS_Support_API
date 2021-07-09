import websocket
import requests
import json
import threading, time

class VCSBanPick:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open("config.json") as config_file:
            self._config = json.load(config_file)
        f = open("demofile2.txt", "a")
        self.load_config()
        # websocket.enableTrace(True)
        self.BanState  = [0,5,1,6,2,7,8,3,9,4]
        self.PickState = [0,5,6,1,2,7,8,3,4,9]
        self.BanNum = 0
        self.PickNum = 0
        self.Timer = 0
        self.Ban = []
        self.Pick = []        
        self.StateArrow = str(self.PathArrow + "Neutral.png")  
        self.TeamName = ["",""]
        self.TeamPlayer = []
        self.Active = False
        self.ClearData()
        self.connect()
        

    def connect(self):
        ws = websocket.WebSocketApp("ws://" + self.ip +":" + self.port ,
                on_open = self.on_open,
                on_message = self.on_message,
                on_error = self.on_error,
                on_close = self.on_close)
        wst = threading.Thread(target=ws.run_forever)
        wst.start() 

    def load_config(self):
        self.ip = self._config["OBS_IP"]
        self.port = self._config["Banpick_Port"]
        vmip = self._config["Vmix_IP"]
        vmport = self._config["Vmix_Port"]
        self.Url = "http://" + vmip + ":" + vmport + "/api/?Function="
        self.PathBan = self._config["Ban_Animation"]
        self.PathLine = self._config["Ban_Line"]
        self.PathArrow = self._config["State_Arrow"]
        self.PathPick = self._config["Pick_Animation"]
        self.PathC = self._config["Champ_Center"]
        self.PathL = self._config["Champ_Loading"]
        self.PathS = self._config["Champ_Square"]

    def on_message(self, ws, message):
        data = json.loads(message)
        if(data["eventType"]=="heartbeat"): return
        if(data["eventType"]=="newState"): 
            self.parseState(data["state"])
        if(data["eventType"]=="newAction"):
            self.parseAction(data["action"])
        if(data["eventType"]=="champSelectStarted"):
            self.CSStarted()
        if(data["eventType"]=="champSelectEnded"):
            self.CSEnded()

    def CSStarted(self):    
        self.ClearData()             
        self.Active = True       
        self.BanNum = 0
        self.PickNum = 0
        self.Ban[0]["Overlay"] = str(self.PathBan + "BAN00001.png")
        self.Ban[0]["Line"] =  str(self.PathLine + "Picking.png")      
        self.ClearData()

    def CSEnded(self):
        self.Active = False
        self.BanNum = 0
        self.PickNum = 0

    def ClearData(self):
        self.Ban = []
        self.Pick = []
        self.TeamName = ["",""]
        self.TeamPlayer = []
        self.Timer = 0
        self.StateArrow = str(self.PathArrow + "Neutral.png")
        for i in range(10):
            Ban = {
                "Overlay": str(self.PathBan + "None.png"),
                "Champion": str(self.PathS + "None.png"),
                "Line": str(self.PathLine + "Pick.png")
            }
            Pick = {
                "Name" : "PLAYER",
                "Overlay": str(self.PathPick + "None.png"),
                "ChampionC": str(self.PathC + "None.png"),
                "ChampionL": str(self.PathL + "None.png"),
                "ChampionS": str(self.PathS + "None.png"),
            }
            Name = ""
            self.Ban.append(Ban)
            self.Pick.append(Pick)
            self.TeamPlayer.append(Name)

    def parseAction(self,data):
        self.restart_27()
        if (data["state"]=="none"):
            self.Active = True
            self.ClearData()            
            self.Ban[0]["Overlay"] = str(self.PathBan + "BAN00001.png")
            self.Ban[0]["Line"] =  str(self.PathLine + "Picking.png")      

        if (data["state"]=="ban"):
            current_Ban = self.BanState[self.BanNum]
            self.Ban[self.BanState[self.BanNum]]["Champion"] = str(self.PathS + data["data"]["champion"]["idName"] + "_0.jpg")
            self.Ban[self.BanState[self.BanNum]]["Overlay"] = str(self.PathBan + "None.png")       
            self.Ban[self.BanState[self.BanNum]]["Line"] = str(self.PathLine + "Picked.png")       
            if (self.BanState[self.BanNum] == 7):
                self.Pick[0]["Overlay"] = str(self.PathPick + "PICK00001.png")
                self.BanNum += 1
                return
            elif (self.BanState[self.BanNum] == 4):
                self.Pick[8]["Overlay"] = str(self.PathPick + "PICK00001.png")
                return
            self.Ban[self.BanState[self.BanNum + 1]]["Overlay"] = str(self.PathBan + "BAN00001.png")
            self.Ban[self.BanState[self.BanNum + 1]]["Line"] = str(self.PathLine + "Picking.png")
            self.BanNum += 1
        
        if (data["state"]=="pick"): 
            self.Pick[self.PickState[self.PickNum]]["Overlay"] = str(self.PathPick + "None.png")
            self.Pick[self.PickState[self.PickNum]]["ChampionC"] = str(self.PathC + data["data"]["champion"]["idName"] + "_centered_splash.jpg")
            self.Pick[self.PickState[self.PickNum]]["ChampionL"] = str(self.PathL + data["data"]["champion"]["idName"]+ "_0.jpg")
            self.Pick[self.PickState[self.PickNum]]["ChampionS"] = str(self.PathS + data["data"]["champion"]["idName"]+ "_0.jpg"),
            if (self.PickState[self.PickNum] == 7):
                self.Ban[8]["Line"] = str(self.PathLine + "Picking.png")
                self.Ban[8]["Overlay"] = str(self.PathBan + "BAN00001.png")
                self.PickNum += 1
                return       
            self.PickNum += 1
            if (self.PickNum == 9):
                self.play_60()
            self.Pick[self.PickState[self.PickNum]]["Overlay"] = str(self.PathPick + "PICK00001.png")

    def parseState(self,data):
        if (not self.Active): return
        if (data["champSelectActive"] != True): return
        # if (data["state"]["state"]==""):
        if (data["blueTeam"]["isActive"]==True and data["redTeam"]["isActive"]==True):
            self.StateArrow = str(self.PathArrow + "Neutral.png")        
        elif (data["blueTeam"]["isActive"]==True):
            self.StateArrow = str(self.PathArrow + "Blue.png")
        elif (data["redTeam"]["isActive"]==True):
            self.StateArrow = str(self.PathArrow + "Red.png")
        else:
            self.StateArrow = str(self.PathArrow + "Neutral.png")
        self.Timer = data["timer"]
        for i in range(0,5):
            if (data["blueTeam"]["picks"] == []): return
            self.TeamPlayer[i] = str(data["blueTeam"]["picks"][i]["displayName"]).split(' ')
            if (data["blueTeam"]["picks"][i]["champion"]["idName"] != ""):
                self.Pick[i]["ChampionC"] = str(self.PathC + data["blueTeam"]["picks"][i]["champion"]["idName"] + "_centered_splash.jpg")
                self.Pick[i]["ChampionL"] = str(self.PathL + data["blueTeam"]["picks"][i]["champion"]["idName"] + "_0.jpg")
                self.Pick[i]["ChampionS"] = str(self.PathS + data["blueTeam"]["picks"][i]["champion"]["idName"] + "_0.jpg")            
        for i in range(5,10):
            if (data["redTeam"]["picks"] == []): return
            self.TeamPlayer[i] = str(data["redTeam"]["picks"][i%5]["displayName"]).split(' ')
            if (data["redTeam"]["picks"][i%5]["champion"]["idName"] != ""):
                self.Pick[i]["ChampionC"] = str(self.PathC + data["redTeam"]["picks"][i%5]["champion"]["idName"] + "_centered_splash.jpg")
                self.Pick[i]["ChampionL"] = str(self.PathL + data["redTeam"]["picks"][i%5]["champion"]["idName"] + "_0.jpg")
                self.Pick[i]["ChampionS"] = str(self.PathS + data["redTeam"]["picks"][i%5]["champion"]["idName"] + "_0.jpg")

        for i in range(0,5):
            if (i==4):
                self.TeamName[0]=self.TeamPlayer[i][0]
                for i in range(0,5):
                    self.TeamPlayer[i].remove(self.TeamName[0])
                break
            if (self.TeamPlayer[i][0]!=self.TeamPlayer[i+1][0]):
                break
                    
        for i in range(5,10):
            if (i==9):
                self.TeamName[1]=self.TeamPlayer[i][0]
                for i in range(5,10):
                    self.TeamPlayer[i].remove(self.TeamName[1])
                break
            if (self.TeamPlayer[i][0]!=self.TeamPlayer[i+1][0]):
                break
        for i in range(10):
            self.TeamPlayer[i] = ' '.join(self.TeamPlayer[i])

    def restart_27(self):
        url = self.Url + "Play&Input=Timer27"
        requests.get(url)
        url = self.Url + "Restart&Input=Timer27"
        requests.get(url)

    def play_60(self):
        url = self.Url + "OverlayInput2In&Input=Timer60"
        requests.get(url)
        url = self.Url + "Play&Input=Timer60"
        requests.get(url)
        url = self.Url + "Restart&Input=Timer60"
        requests.get(url)

    def on_error(self, ws, error):
        self.connect()

    def on_close(self, ws):
        self.ClearData()
        print("Connection closed!")

    def on_open(self, ws):
        print("Connected to: " + self.ip)
