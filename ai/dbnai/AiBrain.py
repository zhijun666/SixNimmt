class Brain:
    def __init__(self):
        self.rows = []
        self.cards = []

    """
    Basic Operations:
    """
    def GetRowsInfo(self, rows):
        self.rows = self.rows + rows
    
    def GetCardsInfo(self, cards):
        self.cards = self.cards + cards

    def GetLastCards_Rows(self):
        last_cards = [row[-1] for row in self.rows]
        return last_cards

    def GetRowsLen(self):
        row_len = [len(row) for row in self.rows]
        return row_len

    def SelCard(self, magnitude = 'min', operator = '>', value = None): #True / False
        """
        Return Type:
        - if can find satisfied value:
            return Index
        - if can't find satisfied value:
            return None
        Variable Format:
        - magnitude: 'min', 'max'
        - operator: '>', '<'
        - value: int_number
        """
        cards_valid = []
        if operator == '>':
            cards_valid = [card for card in self.cards if card > value]
            pass
        elif operator == '<':
            cards_valid = [card for card in self.cards if card < value]
            pass
        else:
            pass
        
        if len(cards_valid) == 0:
            return None

        if magnitude == 'min':
            card_min = min(cards_valid)
            return self.cards.index(card_min)
            
        elif magnitude == 'max':
            card_max = max(cards_valid)
            return self.cards.index(card_max)
        else:
            pass

    def GetExtremValue(self, mode, lenth):
        """
        Input format:
        -mode: 'min', 'max'
        -lenth: int_num
        """ 
        cards_val = []
        for row in self.rows:
            if len(row) == lenth:
                cards_val.append(row[-1])
        if mode == 'min':
            return min(cards_val)
        elif mode == 'max':
            return max(cards_val)
        else:
            pass
    """
    Game Strategies:
    """
    def LargerMinimum(self):
        """
        Details:
        - choose the card that is larger than the smallest value
        Return Type:
        - if can find satisfied value:
            return Index
        - if can't find satisfied value:
            return None
        """
        last_cards = self.GetLastCards_Rows()
        minimum_num = sorted(last_cards)[0]
        card_index = self.SelCard('min','>',minimum_num)
        return card_index

    def LargerSecondMin(self):
        """
        Details:
        - choose the card that is larger than the second small value
        Return Type:
        - if can find satisfied value:
            return Index
        - if can't find satisfied value:
            return None
        """
        last_cards = self.GetLastCards_Rows()
        sec_min_num = sorted(last_cards)[1]
        card_index = self.SelCard('min','>',sec_min_num)
        return card_index

    def EvalDangerousRows(self):
        """
        Details:
        - Find the card value which is smaller than the last card value of dangerous row
        Return Type:
        -if find dangerous row and can find satisfied value:
            return Index
        -if find dangerous row but can't find satisfied value:
            return None
        -if not neccessary:
            return False
        """
        danger_last_cards = []
        for row in self.rows:
            if len(row) == 5:
                danger_last_cards.append(row[-1])
        if len(danger_last_cards) == 0:
            return False
        else:
            card_index = self.SelCard('max', '<', min(danger_last_cards))
            return card_index
        
    
    def EvalRowsLenDiff(self):
        """
        Return Type:
        -if can find a saisfied value:
            return Index
        -if can't find a satisfied value:
            return None
        -if not neccessary:
            return False
        """
        row_len = self.GetRowsLen()
        long_len = max(row_len)
        short_len = min(row_len)
        if (long_len - short_len) >= 3:
            long_val = self.GetExtremValue('min', long_len)
            short_val = self.GetExtremValue('max', short_len)
            if long_val > short_val:
                #Choose the card that has the value < long_val
                return self.SelCard('max', '<', long_val)
            else:
                #Choose the card that has the value > short_val
                return self.SelCard('min', '>', short_val)
        else:
            return False
    def PickSmallest(self):
        """
        Details:
        - this is the contingency plan, choose the smallest card
        Return Type:
        - return Index
        """
        return self.SelCard('min', '>', 0)
    
    """
    Analyze Procedure:
    """
    def AnalyzeCardChoice(self):
        card_pick = None
        card_pick = self.EvalDangerousRows()
        """
        Stage:
        - evaluate the dangerous rows
        """
        if type(card_pick) == int:
            return card_pick
        elif card_pick == None:
            return self.PickSmallest()
        elif card_pick == False:
            """
            stage:
            - evaluate the potential dangerous rows
            """
            card_pick = self.EvalRowsLenDiff()
            if type(card_pick) == int:
                return card_pick
            elif (card_pick == None) or (card_pick == False):
                """
                stage:
                - to choose card safely
                """
                card_pick = self.LargerSecondMin()
                if type(card_pick) == int:
                    return card_pick
                elif card_pick == None:
                    """
                    stage:
                    - choose a card not very safe
                    """
                    card_pick = self.LargerMinimum()
                    if type(card_pick) == int:
                        return card_pick
                    elif card_pick == None:
                        return self.PickSmallest()

    def ChooseRow(self, rows):
        """
        Return Type:
        - index 
        """
        rows_info = [] + rows
        rows_score = [0,0,0,0]
        for i, row in enumerate(rows_info):
            for card in row:
                if card == 55:
                    rows_score[i] = rows_score[i] + 7
                elif card%10 == 5:
                    rows_score[i] = rows_score[i] + 2
                elif card%10 == 0:
                    rows_score[i] = rows_score[i] + 3
                elif card/10 == card%10:
                    rows_score[i] = rows_score[i] + 5
                else:
                    rows_score[i] = rows_score[i] + 1
        return rows_score.index(min(rows_score)) 


"""
Following code are for debuging:
"""
"""
rowsInfo = [[1,3,89],[5] ,[88,90,91,100,102] ,[55,56,58,59,66]]
rowsInfo = [[1,3,89],[50] ,[88,90,91,100] ,[55,56,58,59]]
cardsInfo = [32, 7, 99, 70, 65, 102, 37] 
brain = Brain()
brain.GetRowsInfo(rowsInfo)
brain.GetCardsInfo(cardsInfo)

def TestSelCard():
    brain.cards = [60, 2, 5, 10, 80, 70, 7, 104 ,100]
    card_index = brain.SelCard('max', '<', 10)
    print '\n', brain.cards
    if card_index != None: 
        print "Card Index is: ", card_index, '\n', 'Card Number is: ', brain.cards[card_index] 
    else:
        print "Card Index Return is: ", card_index, '\n'
    
    card_index = brain.SelCard('min', '>', 60)
    if card_index != None: 
        print "Card Index is: ", card_index, '\n', 'Card Number is: ', brain.cards[card_index] 
    else:
        print "Card Index Return is: ", card_index, '\n'

    card_index = brain.SelCard('min', '>', 104)
    if card_index != None: 
        print "Card Index is: ", card_index, '\n', 'Card Number is: ', brain.cards[card_index] 
    else:
        print "Card Index Return is: ", card_index, '\n'
    print "Test Finished, Successed!!!\n"
    brain.cards = []

def TestStrategyOne():
    print "\nThis is for testing LargerSecondMin:"
    print "Reutn value is: ", brain.LargerSecondMin()
    print "Test Successed\n" 

def TestEvalDangerRows():
    print "\ncards:", brain.cards
    print "Last cards on the table are: ", brain.GetLastCards_Rows()
    print "This is for testing EvalDangereRows:"
    print "Reutn value is: ", brain.EvalDangersRows()
    print "Test Successed\n" 

def TestEvalRowsLenDiff():
    print "\ncards: ", brain.cards, '\nsorted cards: ', sorted(brain.cards)
    for i, row in enumerate(brain.rows):
        print "No.", i, "Row: ", row
    print "This is for testing EvalRowsLenDiff:"
    print "The return value is: ", brain.EvalRowsLenDiff()
    print "Test Successed\n" 
"""