#!/usr/bin/env python
import sys
import random
import logging
import os
class AI:
    def __init__(self):
        self.name = ''
        self.cards = []
        self.logFileName = os.path.join(os.path.dirname(__file__), 'log')
        logging.basicConfig(filename = self.logFileName, level=logging.INFO)
    def InfoSetup(self, setupData):
        pass
    def InfoNewGame(self, newGamedata):
        self.cards = newGamedata[:]
        pass
    def InfoGame(self, gameData):
        self.infoGame = gameData
        pass
    def InfoMove(self, cardData):
        pass
    def InfoScore(self, scoreData):
        pass
    def InfoGameEnd(self, gameEndData):
        pass
    def CmdPickCard(self):
        self.cards.sort()
        cardc = self.cards[:]
        data = self.infoGame["rows"]
        sum1 = self.Xscore(data)
        tail = []
        lens = []
        prob = []
        for i in range(4):
            tail.append(data[i][-1])
            lens.append(len(data[i]))
        tailsort = tail[:]
        tailsort.sort()
        tailsort.append(1000000)
        flag = True
        for j in self.cards:
            prob.append(2)
        for k in range(len(cardc)):
            if cardc[k] < tailsort[0]:
                prob[k] *= 20
            else:
                for a in range(4):
                    if cardc[k] < tailsort[a+1] and flag:
                        prob[k] *= (len(data[tail.index(tailsort[a])]))
                        prob[k] *= (sum1[tail.index(tailsort[a])] )
                        flag = False
            
                
        return self.cards.pop(prob.index(min(prob)))

    def Xscore(self,data):
        sum1 = []
        for i in range(4):
            rowdata = data[i]
            rowsum = 0
            for i in rowdata:
                if i == 55:
                    rowsum +=7
                elif i%11 == 0:
                    rowsum += 5
                elif i%10 == 0:
                    rowsum += 3
                elif i%5 == 0:
                    rowsum += 2
                else:
                    rowsum += 1
            sum1.append(rowsum)
        return sum1
    def CmdPickRow(self):
        data = self.infoGame["rows"]
        sum1 = self.Xscore(data)
        return sum1.index(min(sum1))
    def ProcessInfo(self):
        line = sys.stdin.readline()
        if line == '':
            logging.info('No Input')
            sys.exit(1)
        data = line.strip().split('|')
        logging.info("Get Info " + str(line))
        if data[0] == 'INFO':
            if data[1] == 'SETUP':
                self.InfoSetup(eval(data[2]))
            elif data[1] == 'NEWGAME':
                self.InfoNewGame(eval(data[2]))
            elif data[1] == 'GAME':
                self.InfoGame(eval(data[2]))
            elif data[1] == 'MOVE':
                self.InfoMove(eval(data[2]))
            elif data[1] == 'SCORE':
                self.InfoScore(eval(data[2]))
            elif data[1] == 'GAMEEND':
                self.InfoGameEnd(eval(data[2]))
                return False
        elif data[0] == 'CMD':
            if data[1] == 'PICKCARD':
                self.Send(self.CmdPickCard())
            elif data[1] == 'PICKROW':
                self.Send(self.CmdPickRow())
        return True
    def Send(self, data):
        logging.info('Send Info ' + str(data))
        print str(data)
        sys.stdout.flush()
    def Start(self):
        while True:
            if not self.ProcessInfo():
                break

if __name__ == '__main__':
    ai = AI()
    ai.Start()
