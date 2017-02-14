from subprocess import Popen, PIPE
import json
import os
import random
import time
import sys

class Ladder:
    def __init__(self):
        self.baseDir = os.path.dirname(__file__)
        if os.path.exists(os.path.join(self.baseDir, 'playerdata.json')):
            with open(os.path.join(self.baseDir, 'playerdata.json')) as f:
                self.playerData = json.load(f)
        else:
            self.playerData = {}
        with open(os.path.join(self.baseDir, ('playerlist.json'))) as f:
            self.playerList = json.load(f)
        self.playerNameList = []
    def Setup(self):
        for p in self.playerList:
            for name, val in self.playerData.items():
                if os.path.dirname(p["path"]) == os.path.dirname(val["path"]):
                    val["path"] = p["path"]
                    self.playerData[p["name"]] = self.playerData.pop(name)
                    break
            else:
                self.playerData[p["name"]] = {"path":p["path"], "score":[1000]*10, "broken":"false"}
            proc = Popen(['python', os.path.join(self.baseDir, 'NimmtTest.py'), p["path"]], stdout=PIPE)
            result, err = proc.communicate()
            if err != None or "failed" in result:
                self.playerData[p["name"]]["broken"] = "true"
            else:
                self.playerData[p["name"]]["broken"] = "false"
        self.Save()
    def Save(self):
        for val in self.playerData.values():
            for i in range(len(val["score"])-1):
                val["score"][i] = int(val["score"][i])
            val["score"][9] = sum(val["score"][:9])/9
        with open(os.path.join(self.baseDir, 'playerdata.json'), 'w') as f:
            json.dump(self.playerData, f, indent=2)
    def RunOneGame(self, players):
        args = ['python', os.path.join(self.baseDir, 'SixNimmt.py'), '--quiet', '--official', '-s', '500']
        for p in players:
            args.append(p)
        proc = Popen(args, stdout=PIPE)
        result = proc.communicate()[0]
        return json.loads(result)
    def RunRandomGame(self):
        playerNum = random.randint(2,min(10, len(self.playerData)))
        players = random.sample([p for p in self.playerData if self.playerData[p]["broken"] == "false"], playerNum)
        result = self.RunOneGame(players)
        self.UpdateScore(result)
    def UpdateScore(self, result):
        playerNum = len(result)
        totalScore = sum(result.values())
        if "exampleai" not in result:
            totalWeight = sum([1.0/self.playerData[p]["score"][playerNum-2] for p in result])
            for p, score in result.items():
                self.playerData[p]['score'][playerNum-2] -= 0.05*(self.playerData[p]["score"][playerNum-2] - 1.0/(float(score) / totalScore * totalWeight))
        else:
            exampleScore = result["exampleai"]
            for p, score in result.items():
                if p != "exampleai":
                    self.playerData[p]['score'][playerNum-2] -= 0.05*(self.playerData[p]['score'][playerNum-2] - 1.0/(float(score) / exampleScore * (1.0/1000)))

    def Start(self, rounds = 10):
        self.Setup()
        for r in range(rounds):
            for i in range(50):
                self.RunRandomGame()
            print time.strftime("%m/%d %H:%M:%S")
            self.Save()

if __name__ == "__main__":
    ladder = Ladder()
    if len(sys.argv) == 2:
        rounds = int(sys.argv[1])
    else:
        rounds = 10
    ladder.Start(rounds)

