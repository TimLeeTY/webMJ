from random import choices
from string import ascii_uppercase
import numpy as np


class MJgame():
    def __init__(self, players):
        if len(players) != 4:
            raise ValueError('must have 4 players')
        self.players = players
        self.setType = [('suit', int), ('value', int)]
        self.handSize = 13  # Must be 1 mod 3
        self.deck = np.array(
            [(s, v) for s in range(5) for v in range(9) for k in range(4)
             if s < 3 or (s == 3 and v < 4) or (s == 4 and v < 3)], dtype=self.setType)
        np.random.shuffle(self.deck)
        self.playerDict = dict(zip(self.players, range(4)))
        self.start = 0
        self.dealTiles()

    def export_to_json(self):
        # export all variables to a JSON string
        pass

    def import_from_json(self, JSON_string):
        # import all variables to a JSON string
        pass

    def dealTiles(self):
        self.turn = self.start
        self.whoseTurn = self.players[self.start]
        self.turnNum = 0
        self.setDict = dict(zip(self.players, [[] for i in range(4)]))
        self.discPile = dict(zip(self.players, [[] for i in range(4)]))
        self.actionInd = []
        np.random.shuffle(self.deck)
        self.deckLoc = 14 + 13*3
        hands = np.array(
            [self.deck[1+pos*self.handSize:1+(1+pos)*self.handSize]
             if pos != 0 else self.deck[:self.handSize+1] for pos in range(4)])
        hands = [np.sort(hand, order=['suit', 'value']) for hand in hands]
        hands[0] = np.roll(hands[0], -1, axis=0)
        players = [self.players[(i+self.start) % 4] for i in range(4)]
        self.handDict = dict(zip(players, hands))

    def addSet(self, player, newSet):
        nS = newSet
        newSet = np.array([(a[0], a[1]) for a in nS], dtype=self.setType)
        if self.addGong:
            self.setDict[player].remove(newSet)
            setU, setC = newSet[0], 1
        else:
            setU, setC = np.unique(newSet, return_counts=True)
        uniq, count = np.unique(self.handDict[player], return_counts=True)
        for i, each in enumerate(setU):
            count[uniq == each] -= setC[i]
        self.handDict[player] = [u for i, u in enumerate(uniq) for j in range(count[i])]
        if not self.gongBool:
            addTile = self.discPile[self.players[(self.turn - 1) % 4]].pop()
            self.turn = self.playerDict[player]
            self.whoseTurn = player
        else:
            addTile = newSet[0]
        newSet = np.append(newSet, addTile)
        if self.addGong:
            loc = None
        else:
            loc = sum([len(i) for i in self.setDict[player]])
        self.setDict[player].append(newSet)
        self.actionInd = []
        nS.append([int(addTile['suit']), int(addTile['value'])])
        return(player, nS, loc)

    def draw(self):
        player = self.whoseTurn
        tile = self.deck[self.deckLoc]
        self.deckLoc += 1
        self.handDict[player] = np.append(self.handDict[player], tile)
        self.winBool = self.checkWin(self.handDict[player])
        if self.winBool:
            self.winPlayer = [player]
        self.addGong = any(
            np.array_equal(x, np.array([tile for i in range(3)])) for x in self.setDict[player])
        self.gongBool = np.count_nonzero(self.handDict[player] == tile) == 4 or self.addGong
        if self.gongBool:
            self.actionInd = [0]
            self.sO = [np.array([tile for i in range(3)])]
        tile = [int(tile['suit']), int(tile['value'])]
        return(tile, player, self.winBool, self.gongBool)

    def handSizes(self, player):
        offset = self.playerDict[player]+1
        handSizes = [len(self.handDict[self.players[(i+offset) % 4]]) for i in range(3)]
        return(handSizes)

    def showHand(self, player):
        # player should be authenticated first
        return([[int(tile['suit']), int(tile['value'])] for tile in self.handDict[player]])

    def showDiscards(self):
        discPile = {player: [[int(tile['suit']), int(tile['value'])] for tile in discs]
                    for player, discs in self.discPile.items()}
        return(discPile)

    def showSets(self, p=None):
        if p is None:
            playerSets = {
                player: [[int(tile['suit']), int(tile['value'])] for eachSet in sets
                         for tile in eachSet] for player, sets in self.setDict.items()}
        else:
            playerSets = [
                [int(tile['suit']), int(tile['value'])]
                for eachSet in self.setDict[p] for tile in eachSet]
        return(playerSets)

    def discard(self, tile, player):
        if not (self.whoseTurn == player and len(self.actionInd) == 0):
            raise ValueError('not this players turn')
        self.gongBool, self.winBool, self.addGong = False, False, False
        tile = self.handDict[player][tile]
        self.discTile = tile
        self.discPile[player].append(tile)
        uniq, count = np.unique(self.handDict[player], return_counts=True)
        count[uniq == tile] -= 1
        self.handDict[player] = np.array(
            [u for i, u in enumerate(uniq) for j in range(count[i])])
        self.handDict[player] = np.sort(
            self.handDict[player], order=['suit', 'value'])
        self.turn = (self.turn + 1) % 4
        self.whoseTurn = self.players[self.turn]
        return(self.decideOpt(self.whoseTurn, tile))

    def action(self):
        discTile = [int(self.discTile['suit']), int(self.discTile['value'])]
        if len(self.winPlayer) > 0:
            player = self.winPlayer[0]
            sets = self.setDict[player]
            fullHand = [[int(tile['suit']), int(tile['value'])]
                        for eachSet in sets for tile in eachSet] + self.showHand(player)
            return(player, discTile, 'win', fullHand)
        if len(self.actionInd) == 0:
            player = self.players[(self.turn - 1) % 4]
            return(player, discTile, len(self.discPile[player]) - 1, [])
        else:
            ind = self.actionInd[0]
            playerAction = self.players[(self.turn + ind) % 4]
            sT, sO = self.sT[ind], self.sO[ind]
            return(playerAction, discTile, sT, sO)

    def act(self, player, setInd):
        ind = self.actionInd[0]
        playerAction = self.players[(self.turn + ind) % 4]
        if player == playerAction:
            if setInd == 0 and self.gongBool:
                return(None)
            elif setInd == 0:
                self.actionInd.pop(0)
                return(self.action())
            else:
                newSet = self.sO[ind][setInd-1]
                player, newSet, loc = self.addSet(player, newSet)
                return(player, self.discTile, loc, newSet)
        else:
            raise ValueError('not this players turn')

    def playerWin(self, player, winInd):
        if player != self.winPlayer[0]:
            raise ValueError('player not eligible')
        elif winInd > 0:
            discTile = [int(self.discTile['suit']), int(self.discTile['value'])]
            sets = self.setDict[player]
            fullHand = [[int(tile['suit']), int(tile['value'])]
                        for eachSet in sets for tile in eachSet] + self.showHand(player)
            if self.playerDict[player] != self.start:
                self.start = (self.start + 1) % 4
            self.dealTiles()
            return(player, discTile, '', fullHand)
        elif winInd == 0 and not self.winBool:
            self.winPlayer.pop()
            return(self.action())
        else:
            return(None)

    def decideOpt(self, player, tile):
        s, v = tile['suit'], tile['value']
        sT = [[], [], []]
        sO = [[], [], []]
        self.turnNum += 1
        self.winPlayer = []
        for i in range(3):
            check = self.players[(i+self.playerDict[player]) % 4]
            hand = self.handDict[check]
            if self.checkPlayerWin(check):
                print('player {} can win'.format(check))
                self.winPlayer.append(check)
            uniq, count = np.unique(hand, return_counts=True)
            if count[uniq == tile] >= 2:
                sT[i].append('pong')
                sO[i].append([[int(s), int(v)] for i in range(2)])
                if count[uniq == tile] == 3:
                    sT[i].append('gong')
                    sO[i].append([[int(s), int(v)] for i in range(3)])
            if i == 0 and s < 3:
                for j in [-2, 1]:
                    if 0 <= v+j and v+j < 8:
                        pair = np.array([(s, v+i+j) for i in range(2)], dtype=self.setType)
                        if all(i in uniq for i in pair):
                            sO[0].append([[int(s), int(va['value'])] for va in pair])
                            sT[0].append('run')
                if v != 0 and v != 8:
                    pair = np.array([(s, v-1), (s, v+1)], dtype=self.setType)
                    if all(i in uniq for i in pair):
                        sO[0].append([[int(s), int(va['value'])] for va in pair])
                        sT[0].append('run')
        self.sT, self.sO = sT, sO
        self.actionInd = [i for i in range(2, -1, -1) if len(sT[i]) != 0]
        return(self.action())

    def threeCheck(self, a):
        """ checks if hand can be divided evenly into sets by recursion"""
        if len(a) == 0:
            return(True)
        a = np.sort(a, order=['suit', 'value'])
        if (a[0]['suit'] == a[1]['suit'] == a[2]['suit']):
            if (a[0]['value'] == a[1]['value'] == a[2]['value']):
                return((self.threeCheck(a[3:])))
            if a[0]['suit'] < 3 and (a[0]['value'] == a[1]['value']-1 == a[2]['value']-2):
                return((self.threeCheck(a[3:])))
        return(False)

    def checkPlayerWin(self, player):
        return(self.checkWin(np.append(self.handDict[player], self.discTile)))

    def checkWin(self, hand):
        if len(hand) % 3 != 2:
            raise ValueError('hand wrong size')
        uniq, count = np.unique(hand, return_counts=True)
        for ind, c in enumerate(count):
            if c > 1:
                # Choose pair and check for sets
                count[ind] -= 2
                testArr = np.array([u for i, u in enumerate(uniq) for j in range(count[i])])
                if self.threeCheck(testArr):
                    return(True)
                count[ind] += 2
        return(False)


class GameRoom():
    def __init__(self, maxRooms=10, DEV=False):
        self.rooms = []
        self.roomContent = dict()
        self.activePlayers = []
        if DEV:
            self.rooms = ['TEST']
            self.roomContent['TEST'] = {
                'owner': 'tim',
                'players': ['tim', 'alice', 'bob', 'candice'],
                'playing': False,
                'sid': {}
            }
            self.activePlayers = ['tim', 'alice', 'bob', 'candice']
        self.maxRooms = maxRooms
        self.isFull = False

    def createRoom(self, username):
        if (not self.isFull) and (username not in self.activePlayers):
            roomID = ''.join(choices(ascii_uppercase, k=4))
            while roomID in self.rooms:
                roomID = ''.join(choices(ascii_uppercase, k=4))
            self.rooms.append(roomID)
            self.activePlayers.append(username)
            self.roomContent[roomID] = {}
            self.roomContent[roomID]['owner'] = username
            self.roomContent[roomID]['players'] = [username]
            self.roomContent[roomID]['sid'] = {}
            self.roomContent[roomID]['playing'] = False
            if len(self.rooms) == self.maxRooms:
                self.isFull = True
            return(roomID)
        else:
            raise ValueError('too many rooms active')

    def closeRoom(self, roomID):
        if roomID in self.rooms:
            self.rooms = [i for i in self.rooms if i != roomID]
            self.activePlayers = [i for i in self.activePlayers
                                  if i not in self.roomContent[roomID]['players']]
            del self.roomContent[roomID]

    def addPlayer(self, roomID, username):
        if len(self.roomContent[roomID]['players']) >= 4 or roomID not in self.rooms:
            raise(ValueError('room is full'))
        else:
            if username not in self.activePlayers:
                self.roomContent[roomID]['players'].append(username)
                self.activePlayers.append(username)
                return(self.roomContent[roomID]['players'])
            elif username in self.activePlayers:
                raise(KeyError('player already in another room'))

    def removePlayer(self, roomID, username):
        try:
            if username in self.roomContent[roomID]['players']:
                self.roomContent[roomID]['players'] = \
                    [un for un in self.roomContent[roomID]['players'] if un != username]
                self.activePlayers = [un for un in self.activePlayers if un != username]
                del self.roomContent[roomID]['sid'][username]
                return(self.roomContent[roomID]['players'])
            else:
                raise(ValueError('player not in room'))
        except KeyError:
            pass

    def startGame(self, roomID):
        if len(self.roomContent[roomID]['players']) < 4 or roomID not in self.rooms or \
                self.roomContent[roomID]['playing']:
            raise(ValueError('room not full yet'))
        else:
            self.roomContent[roomID]['games'] = MJgame(self.roomContent[roomID]['players'])
            self.roomContent[roomID]['playing'] = True

    def endGame(self, roomID):
        if self.roomContent[roomID]['playing']:
            self.roomContent[roomID]['playing'] = False
            del self.roomContent[roomID]['games']

    def roomExists(self, roomID):
        return(roomID in self.rooms)

    def playerInRoom(self, roomID, username):
        return(username in self.roomContent[roomID]['players'])

    def roomOwner(self, roomID, username):
        return(username == self.roomContent[roomID]['owner'])

    def game(self, roomID):
        try:
            return(self.roomContent[roomID]['games'])
        except KeyError:
            pass
