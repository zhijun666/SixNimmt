#!/usr/bin/env python
from AiBrain import *
import sys
import random
import logging
import os
class AI: 
    def __init__(self):
        self.name = ''
        self.cards = []
        self.rows = []
        self.logFileName = os.path.join(os.path.dirname(__file__), 'log')
        logging.basicConfig(filename = self.logFileName, level=logging.INFO) #For debug 
    """   
    def GetDangerRows(self):
        danRowsIndex = [ i for i, row in enumerate(self.rows) if len(row) == 5 ]
        return danRowsIndex
    """
    
    def InfoSetup(self, setupData):
        pass
    def InfoNewGame(self, newGamedata):
        self.cards = newGamedata[:]
        pass
    def InfoGame(self, gameData):
        #logging.info("The gameData" + str(gameData["rows"]))
        #self.brain.GetRowsInfo(gameData['rows']) 
        self.rows = gameData['rows']
        pass

    def InfoMove(self, cardData):
        pass
    def InfoScore(self, scoreData):
        pass
    def InfoGameEnd(self, gameEndData):
        pass
    def CmdPickCard(self):
        random.shuffle(self.cards)
        brain = Brain()
        brain.GetRowsInfo(self.rows + [])
        brain.GetCardsInfo(self.cards + [])
        """
        self.brain.GetCardsInfo(self.cards)
        logging.info("cards " + str(self.cards))
        logging.info("Index is Lsec--------------- " + str(self.brain.LargerSecondMin()))
        logging.info("Index is LMin--------------- " + str(self.brain.LargerMinimum()))
        card_index = self.brain.LargerSecondMin()
        logging.info("Index is PICK--------------- " + str(card_index))
        """
        return self.cards.pop(brain.AnalyzeCardChoice())
        
    def CmdPickRow(self):
        return Brain().ChooseRow(self.rows) 
    def ProcessInfo(self):
        line = sys.stdin.readline()
        if line == '':
            logging.info('No Input')
            sys.exit(1)
        data = line.strip().split('|') #delete space
        logging.info("Get Info " + str(line))
        if data[0] == 'INFO':
            if data[1] == 'SETUP':
                self.InfoSetup(eval(data[2])) #eval
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
