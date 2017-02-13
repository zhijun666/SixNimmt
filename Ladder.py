from subprocess import Popen, PIPE
import json
import os
import random

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
                self.playerData[p["name"]] = {"path":p["path"], "score":[1000]*10}
    def Save(self):
        with open(os.path.join(self.baseDir, 'playerdata.json'), 'w') as f:
            json.dump(self.playerData, f)
    def RunOneGame(self, players):
        args = ['python', os.path.join(self.baseDir, 'SixNimmt.py'), '--quiet', '--official', '-s', '500']
        for p in players:
            args.append(p)
        proc = Popen(args, stdout=PIPE)
        result = proc.communicate()[0]
        return json.loads(result)
    def RunRandomGame(self):
        playerNum = random.randint(2,min(10, len(self.playerData)))
        players = random.sample(self.playerData.keys(), playerNum)
        result = self.RunOneGame(players)
        self.UpdateScore(result)
    def UpdateScore(self, result):
        playerNum = len(result)
        totalScore = sum(result.values())
        if "exampleai" not in result:
            totalWeight = sum([1.0/self.playerData[p]["score"][playerNum-2] for p in self.playerData])
            for p, score in result.items():
                self.playerData[p]['score'][playerNum-2] -= 0.05*(self.playerData[p]["score"][playerNum-2] - 1.0/(float(score) / totalScore * totalWeight))
        else:
            exampleScore = result["exampleai"]
            for p, score in result.items():
                if p != "exampleai":
                    self.playerData[p]['score'][playerNum-2] -= 0.05*(self.playerData[p]['score'][playerNum-2] - 1.0/(float(score) / exampleScore * (1.0/1000)))
                    print 0.05*(self.playerData[p]['score'][playerNum-2] - 1.0/(float(score) / exampleScore * (1.0/1000)))

    def Start(self):
        self.Setup()
        for i in range(10):
            self.RunRandomGame()
        print self.playerData
        self.Save()

if __name__ == "__main__":
    ladder = Ladder()
    ladder.Start()

