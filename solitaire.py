
# Import random library module to shuffle playing card deck randomly
import random

# Import colorama library to display colors in terminal
from colorama import Fore, Back, Style

# Initialize suits with color
heart = Fore.RED + "♥" + Style.RESET_ALL
diamond = Fore.RED + "♦" + Style.RESET_ALL
club = Fore.BLACK + "♣" + Style.RESET_ALL
spade = Fore.BLACK + "♠" + Style.RESET_ALL

class PlayingCard:
    '''This class is for creating valid playing cards by assigning values for each rank.

    Attributes:
        rank_name (str): Valid rank name for playing card
        rank_value (int): Assigned values for each card rank
        suit (str): Valid suit for playing card
    '''
    rank_dict = {1: "A", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10",
                11: "J", 12: "Q", 13: "K"}
    
    def __init__(self, rank, suit):
        self.rank_name = self.rank_dict[rank]
        self.suit = suit
        self.rank_value = rank
    
    def isOppositeSuit(self, card):
        '''Returns opposite suit colors.
        Input: The four suits (club, diamond, spade and heart)
        Output: Club and diamond cards are red whilst spade and heart cards are black
        '''
        if self.suit == club or self.suit == spade:
            return card.suit == heart or card.suit == diamond
        else:
            return card.suit == spade or card.suit == club
    
    def isFacedUp(self, card):
        '''Returns faced up card.
        Input: Card
        Output: Card faced up must be opposite color and a rank below previous faced up card
        '''
        return self.rank_value == card.rank_value - 1
    
    def isTransferableToTableauPile(self, card):
        ''' Returns True or False
        Input: Is opposite suit color and is faced up card functions
        Output: True if both inputs are satisfied, otherwise False
        '''
        if card.isOppositeSuit(self) and card.isFacedUp(self):
            return True
        else:
            return False
        
    def __repr__(self):
        '''Returns printable representation of object.'''
        return '{}{}'.format(self.rank_name, self.suit)

class Deck:
    '''This class is to distribute cards between the four different spaces: Stock, Waste, 
       Foundation and Tableau pile.
    
    Attribute:
        deck = [shuffled PlayingCard objects]
    '''
    
    deck_unshuffled = [PlayingCard(rankValue, suit) for rankValue in range(1,14) 
                       for suit in [club, diamond, heart, spade]]
    
    def __init__(self, deck_num=1):
        self.deck = self.deck_unshuffled * deck_num
        random.shuffle(self.deck)
    
    def deal_card(self, card_count):
        '''Returns dealt cards.
        Input: Card count
        Output: Dealt cards to either Tableau or Stock or Waste pile
        '''
        return [self.deck.pop() for x in range(card_count)]
    
    def flipCard(self):
        '''Returns removed flipped card from deck.
        Input: Card
        Output: Removed flipped card from Stock or Waste pile
        '''
        return self.deck.pop()
    
    def __repr__(self):
        '''Returns printable representation of object.'''
        return '{}'.format(self.deck)

class Tableau:
    '''This class is to manage the seven pile of cards and interactions with other spaces.
    
    Attributes:
        Flipped card = {Seven flipped cards in Tableau pile}
        Unflipped card = {Seven unflipped cards in Tableau pile}
    '''
    
    def __init__(self, cardList):
        self.unflipped = {n: cardList[n] for n in range(7)}
        self.flipped = {n: [self.unflipped[n].pop()] for n in range(7)}
    
    def flipCard(self, column):
        '''Flips card under each of the seven columns.
        Input: Card
        Output: Flipped card for each column
        '''
        if len(self.unflipped[column]) > 0:
            self.flipped[column].append(self.unflipped[column].pop())
    
    def addCard(self, card, column):
        '''Adds valid card to each of the Tableau columns.
        Input: Permitted card and column specified by player
        Output: Added permitted card under specified column
        '''
        tableau_column = self.flipped[column]
        if len(tableau_column) > 0 and tableau_column[-1].isTransferableToTableauPile(card[0]):
            tableau_column.extend(card)
            return True
        elif len(tableau_column) == 0 and card[0].rank_value == 13:
            tableau_column.extend(card)
            return True
        else:
            return False
        
    def tableau_pile_length(self):
        '''Returns longest tableau pile length.'''
        return max([len(self.unflipped[n]) + len(self.flipped[n]) for n in range(7)])
    
    def tableauCol_to_tableauCol(self, col1, col2):
        '''Transfers card from column to column in the Tableau pile.
        Input: Permitted card and column specified by player
        Output: Successful transfer of card specified by player
        '''
        col1_card = self.flipped[col1]
        
        for i in range(len(col1_card)):
            if self.addCard(col1_card[i:], col2):
                self.flipped[col1] = col1_card[:i]
                if i == 0:
                    self.flipCard(col1)
                return True
        return False
    
    def tableau_to_foundation(self, foundation, column):
        '''Transfers card from Tableau to Foundation pile.
        Input: Permitted card and column specified by player
        Output: Successful transfer of card specified by player
        '''
        column_card = self.flipped[column]
        
        if len(column_card) == 0:
            return False 

        if foundation.addCardFoundation(column_card[-1]):
            column_card.pop()
            if len(column_card) == 0:
                self.flipCard(column)
            return True
        else:
            return False
    
    def waste_to_tableau(self, wastepile, column):
        '''Transfers card from Waste to Tableau pile.
        Input: Permitted card and column specified by player
        Output: Successful transfer of card specified by player
        '''        
        try:
            card = wastepile.waste_card[-1]
            if self.addCard([card], column):
                wastepile.popWasteCard()
                return True
            else: 
                return False
        except (IndexError, AttributeError):
            return False

class StockAndWaste:
    '''This class is to manage the cards in the Stock and Waste pile.
    
    Attributes:
        Deck of cards = card deck in Stock and Waste pile
        Waste card = [card in Waste pile]
    '''
    def __init__(self, card_deck):
        self.card_deck = card_deck
        self.waste_card = []
    
    def stock_to_waste(self):
        '''Transfers card from Stock to Waste pile.
        Input: Permitted card and column specified by player
        Output: Successful transfer of card specified by player
        '''
        if len(self.card_deck) + len(self.waste_card) == 0:
            print("No cards left in the Stock pile.")
            return False
        
        if len(self.card_deck) == 0:
            self.waste_card.reverse()
            self.card_deck = self.waste_card.copy()
            self.waste_card.clear()
        self.waste_card.append(self.card_deck.pop())
        return True
   
    def retrieveWaste(self):
        '''Retrieves top card from the Waste pile.'''
        if len(self.waste_card) > 0:
            return self.waste_card[-1]
        else:
            return "Empty"
    
    def retrieveStock(self):
        '''Retrieves number of cards left in Stock pile.'''
        if len(self.card_deck) > 0:
            return '{} cards'.format(len(self.card_deck))
        else:
            return "Empty"
    
    def popWasteCard(self):
        '''Pops a card from the Waste pile.'''
        if len(self.waste_card) > 0:
            return self.waste_card.pop()
        
class Foundation:
    '''This class is to manage the placement of cards in the Foundation pile.
    
    Attributes:
        foundation_stack = {club: [], heart: [], spade: [], diamond: []}
    '''
    def __init__(self):
        self.foundation_stack = {club: [], heart: [], spade: [], diamond: []}
    
    def addCardFoundation(self, card):
        '''Retrieves card from Tableau or Waste pile.
        Input: Ace card in the faced up position in Tableau or top card in Waste pile
        Output: Added card in Foundation stack
        '''
        try:
            stack = self.foundation_stack[card.suit]
        
            if (card.rank_value == 1 and len(stack) == 0) or stack[-1].isFacedUp(card):
                stack.append(card)
                return True                
            else:
                return False
        except (AttributeError, IndexError):
            return False
    
    def retrieveTopCard(self, suit):
        '''Retrieves top card from the Foundation pile.
        Input: Card
        Output: Top card from Foundation pile. If pile is empty, suit rank is returned.
        '''
        stack_card = self.foundation_stack[suit]
        
        if len(stack_card) == 0:
            return suit
        else:
            return self.foundation_stack[suit][-1]
    
    def winningMessage(self):
        '''Notifies player if game won.
        Input: Empty Tableau stack
        Output: Printed display of congratulatory message when True
        '''
        for suit, tableau_stack in self.foundation_stack.items():
            if len(tableau_stack) == 0:
                return False
            
            card = tableau_stack[-1]
            if card.rank_value != 13:
                return False
        
        return True

class Help:
    '''This class is to display help menu for user/player input.'''
    def helpMenu():
        '''Provides help menu to illustrate command key functions and input syntax.'''
        print (Fore.MAGENTA + '''\n★★★ HELP MENU ★★★
        Transfers card from Waste to Foundation pile - w2f 
        Transfers card from Waste to Tableau column pile - w2t # 
        Transfers card from Stock to Waste pile - s2w
        Transfers card from Tableau column to Foundation pile - t2f # 
        Transfers card from Tableau column to another column - t2t # # 

        Please replace # with a valid integer to specify column number 
        and ensure no space after.\n''' + Style.RESET_ALL)

class Solitaire:
    '''This class is to display solitaire board set up.'''
    def gameEnv(tableau, foundation, stockwaste):
        '''Displays current game environment.'''
        print("-------------------------------------------------------------------------\nWASTE \t STOCK \t\t\t\t FOUNDATION")
        print("{}\t{}\t\t{}\t{}\t{}\t{}".format(stockwaste.retrieveWaste(), stockwaste.retrieveStock(),
                                               foundation.retrieveTopCard(club), foundation.retrieveTopCard(heart),
                                               foundation.retrieveTopCard(spade), foundation.retrieveTopCard(diamond)))
        print("\nTABLEAU\n\t1\t2\t3\t4\t5\t6\t7\n")

        # Display unflipped cards initially then the flipped cards.
        for n in range(tableau.tableau_pile_length()):
            s = ''
            for x in range(7):
                unflipped_card = tableau.unflipped[x]
                flipped_card = tableau.flipped[x]
                if len(unflipped_card) > n:
                    s += Fore.BLUE + '\tX' + Style.RESET_ALL
                elif len(unflipped_card) + len(flipped_card) > n:
                    s += '\t' + str(flipped_card[n - len(unflipped_card)])
                else:
                    s += '\t'
            print(s)
        print("-------------------------------------------------------------------------\n")

class Engine:
    '''This class is to initialize gameplay.'''
    def engine():
        '''Loops gameplay and user/player interactions.'''
        deck1 = Deck()
        tAbleau = Tableau([deck1.deal_card(n) for n in range (1,8)])
        stock_waste = StockAndWaste(deck1.deal_card(24))
        foun = Foundation()
        print('-------------------------------------------------------------------------\n')
        print(Fore.CYAN + "\t\t▂ ▅ ▆ ▇ ᗯEᒪᑕOᗰE TO ᔕOᒪITᗩIᖇE ▇ ▆ ▅ ▂" + Style.RESET_ALL + "\n")
        Solitaire.gameEnv(tAbleau, foun, stock_waste)
        Help.helpMenu()

        while not foun.winningMessage():
            player_input = input("Enter a command key (Type 'quit' to exit game): ").lower()
            print('\n*************************************************************************')
            Help.helpMenu()

            if player_input == "quit":
                print(Fore.RED + "Game has ended!" + Style.RESET_ALL + "\n")
                break
            elif player_input == 'w2f':
                if foun.addCardFoundation(stock_waste.retrieveWaste()):
                    stock_waste.popWasteCard()
                    Solitaire.gameEnv(tAbleau, foun, stock_waste)
                else:
                    print(Fore.RED + 'Invalid move: Unable to transfer card from Waste to Foundation pile.' + Style.RESET_ALL + '\n')
            elif 'w2t' in player_input and len(player_input) == 5:
                if tAbleau.waste_to_tableau(stock_waste, int(player_input[-1]) - 1):
                    Solitaire.gameEnv(tAbleau, foun, stock_waste)
                else:
                    print(Fore.RED + 'Invalid move: Unable to transfer card from Waste to Tableau column.' + Style.RESET_ALL + '\n')
            elif player_input == 's2w':
                if stock_waste.stock_to_waste():
                    Solitaire.gameEnv(tAbleau, foun, stock_waste)
            elif 't2f' in player_input and len(player_input) == 5:
                if tAbleau.tableau_to_foundation(foun, int(player_input[-1]) - 1):
                    Solitaire.gameEnv(tAbleau, foun, stock_waste)
                else:
                    print(Fore.RED + 'Invalid move: Unable to transfer card from Tableau to Foundation pile.' + Style.RESET_ALL + '\n')
            elif 't2t' in player_input and len(player_input) == 7:
                t1, t2 = int(player_input[-3]) - 1, int(player_input[-1]) - 1
                if tAbleau.tableauCol_to_tableauCol(t1, t2):
                    Solitaire.gameEnv(tAbleau, foun, stock_waste)
                else:
                    print(Fore.RED + 'Invalid move: Unable to transfer card to Tableau column.' + Style.RESET_ALL + '\n')
            else:
                print(Fore.RED + 'Invalid move!' + Style.RESET_ALL + '\n')

        if foun.winningMessage():
            print("🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆")
            print("🏆ᑕOᑎGᖇᗩTᑌᒪᗩTIOᑎᔕ! YOᑌ'ᐯE ᗯOᑎ!🏆")
            print("🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆\n")

if __name__ == "__main__":
    Engine.engine()
