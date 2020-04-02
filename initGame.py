from random import shuffle
import numpy as np


class MJgame():
    def __init__(self, flowers=False, in_dict=None):
        if in_dict is not None:
            self.import_from_json(in_dict)
        else:
            self.handSize = 13  # Must be 1 mod 3
            self.deck = [i for i in range(34) for j in range(4)]
            if flowers:
                self.deck += [i+34 for i in range(4) for j in range(2)]
            shuffle(self.deck)
            self.start = 0
            self.dealTiles()
            self.sT = [[], [], []]
            self.sO = [[], [], []]

    def import_from_json(self, in_dict):
        self.handSize = in_dict["handSize"]
        self.deck = in_dict["deck"]
        self.start = in_dict["start"]
        self.turn = in_dict["turn"]
        self.turnNum = in_dict["turnNum"]
        self.setDict = in_dict["setDict"]
        self.discPile = in_dict["discPile"]
        self.discTile = in_dict["discTile"]
        self.actionInd = in_dict["actionInd"]
        self.winPlayer = in_dict["winPlayer"]
        self.addGong = in_dict["addGong"]
        self.gongBool = in_dict["gongBool"]
        self.winBool = in_dict["winBool"]
        self.deckLoc = in_dict["deckLoc"]
        self.handDict = in_dict["handDict"]
        self.sT = in_dict["sT"]
        self.sO = in_dict["sO"]

    def dealTiles(self):
        self.turn = self.start
        self.turnNum = 0
        self.setDict = [[] for i in range(4)]
        self.discPile = [[] for i in range(4)]
        self.actionInd = []
        self.winPlayer = []
        self.addGong = False
        self.discTile = None
        self.gongBool = False
        self.winBool = False
        shuffle(self.deck)
        self.deckLoc = 14 + 13*3
        hands = [self.deck[1+pos*self.handSize:1+(1+pos)*self.handSize]
                 if pos != self.start else self.deck[:self.handSize+1] for pos in range(4)]
        hands = [sorted(i) for i in hands]
        hands[0] = hands[0][1:] + hands[0][0:1]
        self.handDict = hands

    def addSet(self, player, newSet):
        if self.addGong:
            self.setDict[player].remove(newSet)
            setU, setC = [newSet[0]], [1]
        else:
            setU, setC = np.unique(newSet, return_counts=True)
        if self.gongBool:
            setC += 1
        uniq, count = np.unique(self.handDict[player], return_counts=True)
        for i, each in enumerate(setU):
            count[uniq == each] -= setC[i]
        self.handDict[player] = [int(u) for i, u in enumerate(uniq) for j in range(count[i])]
        if not self.gongBool:
            addTile = self.discPile[(self.turn - 1) % 4].pop()
            self.turn = player
            loc = sum([len(i) for i in self.setDict[player]])
        else:
            addTile = newSet[0]
            loc = None
        newSet.append(addTile)
        self.setDict[player].append(newSet)
        self.actionInd = []
        return(player, newSet, loc)

    def draw(self):
        player = self.turn
        tile = self.deck[self.deckLoc]
        print("player {} has drawn".format(player))
        self.deckLoc += 1
        self.handDict[player].append(tile)
        self.winBool = self.checkWin(self.handDict[player])
        if self.winBool:
            self.winPlayer = [player]
        self.addGong = any(np.array_equal(x, [tile for i in range(3)])
                           for x in self.setDict[player])
        self.gongBool = self.handDict[player].count(tile) == 4 or self.addGong
        if self.gongBool:
            self.actionInd = [0]
            self.sO = [[[tile for i in range(3)]]]
            self.sT = [['gong']]
        return(tile, player, self.winBool, self.gongBool)

    def handSizes(self, player):
        handSizes = [len(self.handDict[(i+player+1) % 4]) for i in range(3)]
        return(handSizes)

    def showHand(self, player):
        return(self.handDict[player])

    def showDiscards(self):
        return(self.discPile)

    def showSets(self, p=None):
        if p is None:
            return([[tile for s in pSets for tile in s] for pSets in self.setDict])
        else:
            return([tile for s in self.setDict[p] for tile in s])

    def discard(self, tileInd, player):
        if not (self.turn == player and len(self.actionInd) == 0 and
                len(self.handDict[player]) % 3 == 2):
            raise ValueError('not this players turn')
        self.gongBool, self.winBool, self.addGong = False, False, False
        tile = self.handDict[player][tileInd]
        self.discTile = tile
        self.discPile[player].append(tile)
        uniq, count = np.unique(self.handDict[player], return_counts=True)
        count[uniq == tile] -= 1
        self.handDict[player] = sorted(
            [int(u) for i, u in enumerate(uniq) for j in range(count[i])])
        self.turn = (self.turn + 1) % 4
        return(self.decideOpt(tile))

    def action(self):
        if self.gongBool:
            discTile = self.sO[0][0]
        else:
            discTile = self.discTile
        if len(self.winPlayer) > 0:
            player = self.winPlayer[0]
            sets = self.setDict[player]
            fullHand = [tile for eachSet in sets for tile in eachSet] + self.handDict[player]
            return(player, discTile, 'win', fullHand)
        elif len(self.actionInd) > 0:
            ind = self.actionInd[0]
            playerAction = (self.turn + ind) % 4
            sT, sO = self.sT[ind], self.sO[ind]
            return(playerAction, discTile, sT, sO)
        else:
            player = (self.turn - 1) % 4
        return(player, discTile, len(self.discPile[player]) - 1, [])

    def act(self, player, setInd):
        ind = self.actionInd[0]
        playerAction = (self.turn + ind) % 4
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
            if self.winBool:
                discTile = self.handDict[player].pop()
            else:
                discTile = self.discTile
            sets = self.setDict[player]
            fullHand = self.handDict[player] + [tile for eachSet in sets for tile in eachSet]
            print('fullHand ', fullHand)
            if player != self.start:
                self.start = (self.start + 1) % 4
            self.dealTiles()
            return(player, discTile, '', fullHand)
        elif winInd == 0 and not self.winBool:
            self.winPlayer.pop()
            return(self.action())
        else:
            return(None)

    def decideOpt(self, tile):
        player = self.turn
        s, v = tile // 9, tile % 9
        sT = [[], [], []]
        sO = [[], [], []]
        self.turnNum += 1
        self.winPlayer = []
        for i in range(3):
            check = (i+player) % 4
            hand = self.handDict[check]
            if self.checkPlayerWin(check):
                print('player {} can win'.format(check))
                self.winPlayer.append(check)
            uniq, count = np.unique(hand, return_counts=True)
            if count[uniq == tile] >= 2:
                sT[i].append('pong')
                sO[i].append([tile for i in range(2)])
                if count[uniq == tile] == 3:
                    sT[i].append('gong')
                    sO[i].append([tile for i in range(3)])
            if i == 0 and s < 3:
                for j in [-2, 1]:
                    if 0 <= v+j and v+j < 8:
                        pair = [tile+i+j for i in range(2)]
                        if all(i in uniq for i in pair):
                            sO[0].append(pair)
                            sT[0].append('run')
                if v != 0 and v != 8:
                    pair = [tile - 1, tile + 1]
                    if all(i in uniq for i in pair):
                        sO[0].append(pair)
                        sT[0].append('run')
        self.sT, self.sO = sT, sO
        self.actionInd = [i for i in range(2, -1, -1) if len(sT[i]) != 0]
        return(self.action())

    def threeCheck(self, a):
        """ checks if hand can be divided evenly into sets by recursion"""
        if len(a) == 0:
            return(True)
        a = sorted(a)
        if (a[0] == a[1] == a[2]):
            return(self.threeCheck(a[3:]))
        aCheck = a[0]
        if (aCheck // 9 < 3) and (aCheck % 9 < 7):
            if a.count(aCheck+1) > 0 and a.count(aCheck+2) > 0:
                a.remove(aCheck)
                a.remove(aCheck+1)
                a.remove(aCheck+2)
                return(self.threeCheck(a))
        return(False)

    def checkPlayerWin(self, player):
        return(self.checkWin(np.append(self.handDict[player], self.discTile)))

    def checkWin(self, hand):
        if len(hand) % 3 != 2:
            raise ValueError('hand wrong size')
        uniq, count = np.unique(hand, return_counts=True)
        for ind, c in enumerate(count):
            if c >= 2:
                # Choose pair and check for sets
                count[ind] -= 2
                testArr = [u for i, u in enumerate(uniq) for j in range(count[i])]
                if self.threeCheck(testArr):
                    return(True)
                count[ind] += 2
        return(False)
