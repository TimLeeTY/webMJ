from random import shuffle
import numpy as np


class MJgame():
    def __init__(self, flowers=False, in_dict=None):
        """
        Load variables from dictionary object or initialise with new game
        Variables are exported using the __dict__ method and stored as a
        JSON object
        """
        if in_dict is not None:
            self.import_from_json(in_dict)
        else:
            self.deck = [i for i in range(34) for j in range(4)]
            if flowers:
                self.deck += [i+34 for i in range(4) for j in range(2)]
            self.start = 0
            self.wind = 0
            self.dealTiles()
            self.sT = [[], [], []]
            self.sO = [[], [], []]

    def import_from_json(self, in_dict):
        self.deck = in_dict["deck"]
        self.start = in_dict["start"]
        self.turn = in_dict["turn"]
        self.turnNum = in_dict["turnNum"]
        self.setDict = in_dict["setDict"]
        self.typeDict = in_dict["typeDict"]
        self.discPile = in_dict["discPile"]
        self.discTile = in_dict["discTile"]
        self.actionInd = in_dict["actionInd"]
        self.winPlayer = in_dict["winPlayer"]
        self.addGong = in_dict["addGong"]
        self.darkGong = in_dict["darkGong"]
        self.gongBool = in_dict["gongBool"]
        self.winBool = in_dict["winBool"]
        self.deckLoc = in_dict["deckLoc"]
        self.handDict = in_dict["handDict"]
        self.wind = in_dict["wind"]
        self.sT = in_dict["sT"]
        self.sO = in_dict["sO"]

    def dealTiles(self):
        """
        Initialise game specific variables;
        called whenever a game is over
        """
        self.turn = self.start
        self.turnNum = 0
        self.setDict = [[] for i in range(4)]
        self.typeDict = [[] for i in range(4)]
        self.discPile = [[] for i in range(4)]
        self.actionInd = []
        self.winPlayer = []
        self.addGong = []
        self.darkGong = []
        self.discTile = None
        self.gongBool = []
        self.winBool = False
        # shuffle(self.deck)
        handSize = 13
        self.deckLoc = handSize*4+1
        hands = []
        for pos in range(4):
            if pos == self.start:
                hands.append(sorted(self.deck[:handSize+1], reverse=True))
            else:
                relPos = (pos - self.start) % 4
                hands.append(sorted(
                    self.deck[1+relPos*handSize:1+(1+relPos)*handSize], reverse=True))
        hands[self.start] = hands[self.start][1:] + hands[self.start][0:1]
        self.handDict = hands

    def addSet(self, player, newSet, newType):
        """
        Add a set to the corresponding player;
        'Gongs' that occur when a player draws is handled separately
        (hence gongBool and addGong)
        """
        if newType == 'addGong':
            self.setDict[player].remove(newSet)
            self.typeDict[player].remove('pong')
            self.typeDict[player].append('gong')
            newSet = [newSet[0] for i in range(4)]
        elif newType == 'darkGong':
            self.typeDict[player].append('gong')
            newSet = [newSet[0] for i in range(4)]
        else:
            self.typeDict[player].append(newType)
        # remove tiles from hand
        remTiles = [newSet[0]] if newType == 'addGong' else newSet
        for each in remTiles:
            self.handDict[player].remove(each)
        # redirect turn to appropriate player
        if newType not in ['addGong', 'darkGong']:
            addTile = self.discPile[(self.turn - 1) % 4].pop()
            self.turn = player
            newSet.append(addTile)
        loc = sum([len(i) for i in self.setDict[player]])\
            if newType != 'addGong' else None
        self.setDict[player].append(newSet)
        self.actionInd = []
        return(player, newSet, loc)

    def draw(self):
        """
        Draw a tile for the current player;
        no verification as not directly called by client
        Returns values needed to display drawn tile along with
        possibility to perform 'gong' action
        """
        if self.deckLoc == len(self.deck):
            self.start = (self.start+1) % 4
            self.dealTiles()
            return(None, None, False, False)
        player = self.turn
        tile = self.deck[self.deckLoc]
        self.deckLoc += 1
        self.handDict[player].append(tile)
        hand = self.handDict[player]
        sets = self.setDict[player]
        uniq, count = np.unique(hand, return_counts=True)
        # Do win logic
        self.winBool = self.checkWin(self.handDict[player])
        if self.winBool:
            self.winPlayer = [player]
        # Do add gong and dark gong logic
        self.addGong = [int(checkTile) for x in sets for checkTile in uniq
                        if np.array_equal(x, [int(checkTile) for i in range(3)])]
        self.darkGong = [int(i) for i in uniq[count == 4]]
        self.actionInd = [0] if len(self.addGong) + len(self.darkGong) > 0 else []
        self.sT = [['addGong' for i in range(len(self.addGong))] +
                   ['darkGong' for i in range(len(self.darkGong))]]
        self.sO = [[[int(eTile) for i in range(3)]
                    for eTile in np.append(self.addGong, self.darkGong)]]
        self.gongBool = self.addGong + self.darkGong
        print(self.gongBool)
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
            return([[tile for s in pSets for tile in s]
                    for pSets in self.setDict])
        else:
            return([tile for s in self.setDict[p] for tile in s])

    def discard(self, tileInd, player):
        """
        Discard tile for player by index of tile; verifies turn and empty actionInd
        Returns values needed to display discarded tile
        """
        if not (self.turn == player and len(self.actionInd) == 0 and
                len(self.handDict[player]) % 3 == 2):
            raise ValueError('not this players turn')
        self.gongBool, self.winBool, self.addGong = [], False, []
        tile = self.handDict[player][tileInd]
        self.discTile = tile
        self.discPile[player].append(tile)
        self.handDict[player].remove(tile)
        self.handDict[player].sort(reverse=True)
        self.turn = (self.turn + 1) % 4
        return(self.decideOpt(tile))

    def action(self):
        """Returns the next action to be taken based on game state """
        if len(self.gongBool) > 0:
            discTile = self.gongBool
        else:
            discTile = self.discTile
        if len(self.winPlayer) > 0:
            # return win option
            player = self.winPlayer[0]
            sets = self.setDict[player]
            fullHand = [tile for eachSet in sets for tile in eachSet]\
                + self.handDict[player]
            return(player, discTile, 'win', fullHand)
        elif len(self.actionInd) > 0:
            # return action list
            ind = self.actionInd[0]
            playerAction = (self.turn + ind) % 4
            sT, sO = self.sT[ind], self.sO[ind]
            return(playerAction, discTile, sT, sO)
        else:
            # show discarded tile and associated player
            player = (self.turn - 1) % 4
        return(player, discTile, len(self.discPile[player]) - 1, [])

    def act(self, player, setInd):
        """
        Attempt to perform action provided by player;
        set index is based on choices provided by action() above
        Returns values needed to display chosen action
        """
        ind = self.actionInd[0]
        playerAction = (self.turn + ind) % 4
        if player != playerAction:
            raise ValueError('not this players turn')
        if setInd == 0 and len(self.gongBool) > 0:
            self.actionInd = []
            self.gongBool = []
            self.addGong = []
            self.darkGong = []
            return(None, None, None, None)
        elif setInd == 0:
            self.actionInd.pop(0)
            return(self.action())
        else:
            newSet = self.sO[ind][setInd-1]
            newType = self.sT[ind][setInd-1]
            player, newSet, loc = self.addSet(player, newSet, newType)
            return(player, self.discTile, loc, newSet)

    def playerWin(self, player, winInd):
        """
        Handle 'win' action provided by player;
        verifies player is in position to win and handles choice via winInd:
        0: ignore win
        1: win
        """
        if player != self.winPlayer[0]:
            raise ValueError('player not eligible')
        elif winInd > 0:
            maxPoints, fullHand = self.maxPoints(player)
            if self.winBool:
                discTile = self.handDict[player].pop()
                maxPoints['Self Draw'] = 1
            else:
                discTile = self.discTile
            fullHand.remove(discTile)
            if player != self.start:
                if self.start == 3:
                    self.wind = (self.wind + 1) % 4
                self.start = (self.start + 1) % 4
            self.dealTiles()
            return(player, discTile, maxPoints, fullHand)
        elif winInd == 0 and not self.winBool:
            self.winPlayer.pop()
            return(self.action())
        else:
            return(None, None, None, None)

    def decideOpt(self, tile):
        """
        After each discard, decide the available options to rest of the players
        result is passed on to action which decides the order in which these
        actions will be handled
        """
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
                for j in (-2, 1):
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
        """Checks if hand can be divided evenly into sets by recursion """
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
        """Checks if input is a winning hand"""
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

    def partHand(self, hand, sets, types):
        """
        Partitions hand into all winning combinations of sets + 'eyes'
        *Input should be winning hands only*
        """
        if len(hand) % 3 != 2:
            raise ValueError('hand wrong size')
        eye = []
        setArr = []
        typeArr = []
        uniq, count = np.unique(hand, return_counts=True)
        for ind, c in enumerate(count):
            if c >= 2:
                # Choose pair and check for sets
                count[ind] -= 2
                testArr = [int(u) for i, u in enumerate(uniq)
                           for j in range(count[i])]
                setsCheck, typesCheck = self.threePart(testArr)
                for j in range(len(setsCheck)):
                    setArr.append(sets + setsCheck[j])
                    typeArr.append(types + typesCheck[j])
                    eye.append(int(uniq[ind]))
                count[ind] += 2
        return(eye, setArr, typeArr)

    def threePart(self, a):
        """Returns all possible ways to divide tiles into sets of 3 """
        if len(a) == 0:
            return([[]], [[]])
        a = sorted(a)
        setsArr = []
        typesArr = []
        aCheck = a[0]
        if (aCheck == a[1] == a[2]):
            sets, types = self.threePart(a[3:])
            for i in range(len(sets)):
                setsArr.append([[aCheck for j in range(3)]] + sets[i])
                typesArr.append(['pong'] + types[i])
                if a.count(aCheck) == 4:
                    # Avoid double counting when aCheck pongs and runs
                    return(setsArr, typesArr)
        if (aCheck // 9 < 3) and (aCheck % 9 < 7):
            if a.count(aCheck+1) > 0 and a.count(aCheck+2) > 0:
                a.remove(aCheck)
                a.remove(aCheck+1)
                a.remove(aCheck+2)
                sets, types = self.threePart(a)
                for i in range(len(sets)):
                    setsArr.append([[aCheck, aCheck+1, aCheck+2]] + sets[i])
                    typesArr.append(['run'] + types[i])
        return(setsArr, typesArr)

    def pointTally(self, eyes, sets, types, player):
        """
        Checks points for a winning hand:
        - Additive points system
        - Greedy counting; prioritize higher point set combinations, i.e.:
            - All pongs -> all runs -> mix
        Based on rules from en.wikipedia.org/wiki/Hong_Kong_Mahjong_scoring_rules
        """
        winds = [eachSet[0] % 9 for eachSet in sets if 27 <= eachSet[0] < 31]
        dragonSets = [eachSet[0] % 9 for eachSet in sets if eachSet[0] >= 31]
        suits = sorted([eachSet[0]//9 for eachSet in sets] + [eyes//9])
        pointDict = {
            'Common': 1 if all(setType == 'run' for setType in types) else 0,
            'All in Triplets': 3 if
            all(setType in ('pong', 'gong') for setType in types) else 0,
            'All Kong': 13 if
            all(setType == 'gong' for setType in types) else 0,
            'Orphans': 7 if all(s[0] % 9 in (0, 8) and s[0] // 9 < 3 and s[0] == s[1]
                                for s in sets) else 0,
            'Mized Orphans': 1 if
            all(((s[0] % 9 in (0, 8)) or (s[0] // 9 == 3)) for s in sets) else 0,
            'All Honor Tiles': 7 if min(suits) == 3 else 0,
            'All One Suit': 7 if
            suits.count(suits[0]) == len(suits) and suits[0] < 3 else 0,
            'Mixed One Suit': 3 if 0 < suits.count(3) < len(suits) and
            all(suit == suits[0] or suit == 3 for suit in suits) else 0,
            'Great Dragons': 5 if len(dragonSets) == 3 else 0,
            'Small Dragons': 3 if len(dragonSets) == 2 and eyes >= 31 else 0,
            'Three Dragons': len(dragonSets),
            'Great Winds': 13 if len(winds) == 4 else 0,
            'Small Winds': 6 if len(winds) == 3 and 27 <= eyes < 3 else 0,
        }
        pointDict['Winds'] = 0 if pointDict['Small Winds'] != 0 else sum(
            i in winds for i in [self.wind, (player-self.start) % 4])
        fullHand = [tile for eachSet in sets for tile in eachSet] +\
            [eyes for i in range(2)]
        return(pointDict, sum(pointDict.values()), fullHand)

    def maxPoints(self, player):
        hand = self.handDict[player]
        if not self.winBool:
            hand.append(self.discTile)
        sets = self.setDict[player]
        types = self.typeDict[player]
        part = self.partHand(hand, sets, types)
        trackMax = 0
        for i in range(len(part[0])):
            tmpDict, points, tmpHand = self.pointTally(
                part[0][i], part[1][i], part[2][i], player)
            if points >= trackMax:
                pointDict = tmpDict
                fullHand = tmpHand
        deleteKey = [key for key, item in pointDict.items() if item == 0]
        for key in deleteKey:
            del pointDict[key]
        return(pointDict, fullHand)
