#!/usr/bin/env python
import logging
import random
from subprocess import Popen, PIPE, call
import os
import argparse
import re
import sys
import itertools
import json

class AiHandler:
    def __init__(self):
        self.procs = {}
    def AddAi(self, name, path):
        if os.path.exists(path):
            if path.endswith(".py") or path.endswith(".pyc"):
                p = Popen(['python', path], stdin=PIPE, stdout=PIPE, bufsize=0)
            else:
                p = Popen([path], stdin=PIPE, stdout=PIPE, bufsize=0)
            self.procs[name] = p
        else:
            call("make", cwd=os.path.dirname(path))
            if not os.path.exists(path):
                raise Exception("there's no path" + path)
            else:
                p = Popen([path], stdin=PIPE, stdout=PIPE, bufsize=0)
                self.procs[name] = p
    def Send(self, s, player = None):
        if player == None:
            for p in self.procs.values():
                p.stdin.write(s+'\n')
        else:
            self.procs[player].stdin.write(s+'\n')
    def Receive(self, player):
        line = self.procs[player].stdout.readline()
        return line
    def Info(self, subHeader, data, player = None):
        msg = 'INFO|' + subHeader + '|' + json.dumps(data)
        self.Send(msg, player)
    def Cmd(self, subHeader, player = None):
        msg = 'CMD|' + subHeader
        self.Send(msg, player)
        return int(self.Receive(player).strip())

class Player:
    def __init__(self, name, path):
        self.name = name
        self.cards = []
        self.score = 0
        self.path = path
        self.aiHandler = None
    def SetAiHandler(aiHandler):
        self.aiHandler = aiHandler
    def NewGame(self, cards):
        self.cards = cards[:]
        if self.aiHandler != None:
            self.aiHandler.Info('NEWGAME', self.cards, player = self.name)
        else:
            print 'New cards:', self.cards
        
    def PickCard(self):
        if self.aiHandler != None:
            c = self.aiHandler.Cmd('PICKCARD', self.name)
        else:
            print 'Current Card:', sorted(self.cards)
            c = eval(raw_input('Please choose a card to put\n'))
        if c not in self.cards:
            raise Exception("Error! Card {} is played but the player {} does not have it!".format(c, self.name))
        self.cards.remove(c)
        return c

    def PickRow(self):
        if self.aiHandler != None:
            c = self.aiHandler.Cmd('PICKROW', self.name) 
        else:
            print 'Choose a row to pick'
            c = eval(raw_input('Please choose a row\n'))
        if c not in range(4):
            raise Exception("Error! Player {} picked row {} and it's out of range!".format(self.name, c))
        return c
    def Score(self, score):
        self.score += score
    def PrintData(self):
        print "Name: {}, Cards: {}, Score: {}".format(self.name, self.cards, self.score)

class SixNimmtGame:
    def __init__(self, **kwargs):
        self.playerNum = 0
        self.rows = [[],[],[],[]]
        self.players = {}
        self.aiHandler = AiHandler()
        self.broadCast = 0
        with open(os.path.join(os.path.dirname(__file__), "playerlist.json")) as f:
            self.playerList = json.load(f)
        for key, val in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, val)
            else:
                raise Exception("Wrong keyword "+key)

    def AddPlayer(self, path):
        '''
        Add a player in the game
          * path: the path to the AI, could be an alias
        '''
        if os.path.exists(path):
            playerName = path.split('/')[-1].split('.')[0]
        else:
            playerName = path
            for p in self.playerList:
                if p["name"] == path:
                    path = os.path.join(os.path.dirname(__file__),p["path"])
                    break
            else:
                raise Exception("No alias or path {} exists!".format(path))
        if playerName in self.players:
            suffix = 2
            newPlayerName = playerName + str(suffix)
            while newPlayerName in self.players:
                suffix += 1
                newPlayerName = playerName + str(suffix) 
            playerName = newPlayerName
        self.players[playerName] = Player(playerName, path)
        self.playerNum += 1

    def Setup(self):
        self.aiHandler = AiHandler()
        for name in self.players:
            self.aiHandler.AddAi(name, self.players[name].path)
            self.players[name].aiHandler = self.aiHandler
            data = {}
            data["name"] = name
            data["playerNum"] = self.playerNum
            self.aiHandler.Info('SETUP', data, name)

    def OfficialGame(self, rounds = None, score = None):
        self.Setup()
        r = 0
        while True:
            self.deck = list(range(1,105))
            random.shuffle(self.deck)
            roundRows = [self.deck.pop() for i in range(4)]
            hands = [[self.deck.pop() for i in range(10)] for j in range(self.playerNum)]
            for shift in range(self.playerNum):
                hands = hands[-1:] + hands[:-1]
                for i in range(4):
                    self.rows[i] = [roundRows[i]] 
                self.rows.sort(key = lambda x:x[-1], reverse = True)
                idx = 0
                for p in self.players.values():
                    cards = hands[idx]
                    self.BroadCast('{} got {}'.format(p.name, cards))
                    p.NewGame(cards)
                    idx += 1
                for i in range(10):
                    self.NewRound()
            if rounds != None and rounds != 0:
                r += 1
                if r >= rounds:
                    break
            elif score != None:
                if any([p.score > score for p in self.players.values()]):
                    break
            else:
                break
        self.SendGameEndInfo()
            
    def StartTour(self, score):
        self.Setup()
        while True:
            self.NewGame()
            if any([p.score > score for p in self.players.values()]):
                self.SendGameEndInfo()
                break

    def NewGame(self):
        '''
        Create a new game, do not clear score.
        Deal 10 cards for each player
        '''
        self.BroadCast("New Game Begins!")
        self.deck = list(range(1, 105))
        random.shuffle(self.deck)
        for i in range(4):
            self.rows[i] = [self.deck.pop()]
        self.rows.sort(key = lambda x:x[-1], reverse = True)
        for p in self.players.values():
            cards = [self.deck.pop() for i in range(10)]
            self.BroadCast("{} got {}".format(p.name, cards))
            p.NewGame(cards)
        for r in range(10):
            self.NewRound()

    def NewRound(self):
        '''
        A new round of a game.
        Send the game status to all players.
        Request a card from each player
        Process the result
        '''
        self.newCards = []
        self.SendGameInfo()
        for name, p in self.players.items():
            self.newCards.append((name, p.PickCard()))
        self.SendMoveInfo(self.newCards)
        self.ProcessGame()
        
    def ProcessGame(self):
        self.newCards.sort(key = lambda x:x[-1])
        for name, c in self.newCards:
            if c < min([self.rows[i][-1] for i in range(4)]):
                rowNum = self.players[name].PickRow()
                self.BroadCast("{} picked row {}:{}".format(name, rowNum, self.rows[rowNum]))
                self.SendScoreInfo(name, self.rows[rowNum])
                self.players[name].Score(self.CountScore(self.rows[rowNum]))
                self.rows[rowNum] = [c]
                # sort rows based on the last value
                self.rows.sort(key = lambda x:x[-1], reverse=True)
            else:
                for r in self.rows:
                    if c > r[-1]:
                        if len(r) == 5:
                            self.SendScoreInfo(name, r)
                            self.players[name].Score(self.CountScore(r))
                            r[:] = [c]
                        else:
                            r.append(c)
                        break
                else:
                    raise Exception("Value should be in range!")

    def SendGameInfo(self):
        game = {}
        game['rows'] = self.rows
        game['players'] = {}
        for p in self.players:
            game['players'][p] = self.players[p].score
        self.aiHandler.Info('GAME', game)
        self.BroadCast('Current Game:')
        self.BroadCast(game['players'])
        for r in self.rows:
            self.BroadCast(r)

    def SendScoreInfo(self, player, cards):
        data = {}
        data['player'] = player
        data['cards'] = cards[:]
        data['score'] = self.CountScore(cards)
        self.aiHandler.Info('SCORE', data)
        self.BroadCast('Score!')
        self.BroadCast(data)

    def SendMoveInfo(self, cardInfo):
        move = {}
        for name, card in cardInfo:
            move[name] = card
        self.aiHandler.Info('MOVE', move)
        self.BroadCast('Move!')
        self.BroadCast(move)
    
    def SendGameEndInfo(self):
        finalScore = {}
        winner = None
        winScore = -1
        for p in self.players:
            if winner == None or self.players[p].score < winScore:
                winner = p
                winScore = self.players[p].score
            finalScore[p] = self.players[p].score
        self.aiHandler.Info('GAMEEND', finalScore)
        self.BroadCast('The game ends!')
        self.BroadCast('Final score:')
        self.BroadCast('{}'.format(json.dumps(finalScore)), 8)
        self.BroadCast('Winner is {}'.format(winner))

    '''
    Utilities 
    '''
    def CountScore(self, cards):
        score = 0
        for c in cards:
            if c == 55:
                score += 7
            elif c % 11 == 0:
                score += 5
            elif c % 10 == 0:
                score += 3
            elif c % 5 == 0:
                score += 2
            else:
                score += 1
        return score

    def BroadCast(self, s, level = 5):
        if level >= self.broadCast:
            print s
    def PrintData(self):
        print "Current Row:"
        for r in self.rows:
            print r
        print 'New Cards: {}'.format(self.newCards)
        for p in self.players.values():
            p.PrintData()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--score', type=int, default=100, help='the score where the game ends')
    parser.add_argument('--seed', type=int, default=None, help='set random seed to reproduce the game')
    parser.add_argument('-q', '--quiet', action='store_true', help='do not print any detailed info from the game')
    parser.add_argument('--mute', action='store_true', help='do not print any info from the game')
    parser.add_argument('--official', action='store_true', help='use official mode, same cards will be sent to players')
    parser.add_argument('-r', type=int, default = 0, help='only works in official mode, how many rounds you want to run')
    parser.add_argument('aiPaths', nargs='+', help='paths to ai')
    options = parser.parse_args()
    random.seed(options.seed)
    game = SixNimmtGame()
    if options.quiet:
        game.broadCast = 7
    elif options.mute:
        game.broadCast = 10
    # Add players
    for path in options.aiPaths:
        m = re.search('^([0-9]*)\*(.*)', path)
        if m != None:
            for i in range(int(m.group(1))):
                game.AddPlayer(m.group(2))
        else:
            game.AddPlayer(path)
    if not 2 <= game.playerNum <= 10:
        print 'You need 2 to 10 AIs to start the game'
        sys.exit(1)
    if options.official:
        game.OfficialGame(rounds = int(options.r), score = int(options.score))
    else:
        game.StartTour(options.score)
