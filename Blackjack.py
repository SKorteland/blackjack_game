# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 18:34:47 2017

A simple blackjack game

@author: 
"""

from random import shuffle

class Participant(object):
    """A participant in a Blackjack game """
    
    def __init__(self, name, wallet = 0):
        self.wallet = wallet
        self.name = name
        self.hand = Hand()
    
    def deposit(self, amount):
        """ place an amount into the participant's wallet """
        self.wallet += amount
    
    def get_balance(self):
        """ return the particpants balance"""
        return self.wallet
    
    def receive_cards(self, cards):
        """receive cards """
        self.hand.add_cards(cards)
    
    def show_hand(self):
        """ show the hand of cards in posession """
        self.hand.show()
    
    def reset_hand(self):
        """ reset the hand to empty """
        self.hand = Hand()
        
    def open_hand(self):
        """ flip over any cards that were face down """
        self.hand.open_cards()
    
    def is_bust(self):
        return self.hand.is_bust()
    
    def has_blackjack(self):
        return self.hand.is_blackjack()
    
    def get_count(self):
        """ get the blackjack count """
        return self.hand.compute_bj_count()
    
    def __str__(self):
        return self.name

class Player(Participant):
    """A blackjack player"""
    
    def __init__(self, name, wallet = 0):
        Participant.__init__(self, name, wallet)
        self.bet = 0
    
    def pay_bet(self):
        """ pay a bet to the dealer """
        self.wallet -= self.bet
        self.bet = 0
    
    def place_bet(self, amount):
        """ place a bet for a certain amount """
        self.bet = amount
    
    def reset_bet(self):
        self.bet = 0
        
    def get_bet(self):
        return self.bet
    


class Dealer(Participant):
    """ A blackjack dealer"""
    
    def __init__(self, name, wallet = 0):
       Participant.__init__(self, name, wallet)
        
    
    def deal_cards(self, participant, deck, size, face_down = 0):
        """ deal a number of cards from the deck to a participant"""
        cards = deck.draw_cards(size)
        #cover the number of cards that have to be face down
        for i in xrange(0,face_down):
            idx = -1-i
            cards[idx].flip()
            
        participant.receive_cards(cards)
    
    def pay_out(self, player1, payout_type):
        """ pay out to a player """
        if (payout_type == "natural"):
            player1.deposit(1.5 * player1.get_bet())
            player1.reset_bet()
        elif payout_type == "standard":
            player1.deposit(player1.get_bet())
            player1.reset_bet()
        elif payout_type == "standoff":
            player1.reset_bet()
       
        
    def collect_bet(self, player):
        """ collect lost bets """
        player.pay_bet()
        
    def should_hit(self):
        """ 
        determine if the dealer should hit or not
        returns true of the dealer's count is less than 17, returns false
        if the dealer's count is 17 or more 
        """
        
        return self.hand.compute_bj_count() < 17
    
    def first_card_10_or_ace(self):
        rank = self.hand.get_card(0).get_rank()
        return (rank == "Ace" or rank == "10" or
                rank == "Jack" or rank == "Queen" or
                rank == "King")

class Deck(object):
    """ A deck of 52 cards """
    
    def __init__(self):
        self.new_deck()
        
        
    def new_deck(self):
        #create a deck of 52 cards of 4 suits each with 13 ranks
     
        suits = ["Clubs", "Diamonds", "Hearts", "Spades"]
        ranks = ["Ace",  "2", "3", "4", "5", "6", "7", "8",
                 "9", "10", "Jack", "Queen", "King"]
        deck =[Card(rank, suit) for suit in suits for rank in ranks]
        
        self.deck = deck
    
    def shuffle(self):
        """ randomly shuffle the deck of cards """
        shuffle(self.deck)
        
    
    def draw(self):
        """ draw a card from the top of the deck """
        return self.deck.pop()
        
    def draw_cards(self, size):
        """ draw cards from the top  of the deck 
        return a Hand object with the requested number of cards """
        cards = self.deck[-size:]
        self.deck = self.deck[:-size]
        return cards
    
        
    def __len__(self):
        return len(self.deck)
        
    
class Card(object):
    """ a playing card with a rank and suit and associated blackjack value
    The card can be face_up or face_down"""
    
    def __init__(self, rank, suit, face_up= True):
        self.rank = rank
        self.suit = suit
        self.face_up = face_up
        if rank == "Ace":
            self.bj_value = 11
        elif rank == "Jack" or rank == "Queen" or rank == "King":
            self.bj_value = 10
        elif rank in "2 3 4 5 6 7 8 9 10".split():
            self.bj_value = int(rank)
        else:
            #the card has no blackjack value
            self.bj_value = 0
            
    def get_rank(self):
        return self.rank
    
    def get_suit(self):
        return self.suit
    
    def get_bj_value(self):
        return self.bj_value
        
    def flip(self):
        self.face_up = not self.face_up
    
    def is_face_up(self):
        return self.face_up
    
    def __str__(self):
        if self.face_up == True:
            return self.rank + " of " + self.suit
        else:
            return "X"
    
class Hand(object):
    """ A hand of cards in a blackjack game
    Each card can be either open or closed and can be flipped 
    by calling the appropriate method """
    
    def __init__(self, cards= None):
        if cards == None:
            self.cards =[]
        else:
            self.cards = cards
        
    
    def add_cards(self, new_cards):
        """ add card(s) to the hand """
        self.cards.extend(new_cards)
        
    
    def show(self):
        
        for card in self.cards:
            print card
        
        print "Count: %d" %(self.compute_bj_count())
    
    def get_card(self, idx):
        """return the card at position idx"""
        return self.cards[idx]
        
    def open_cards(self):
        """flip over any cards that are face down"""
        for card in self.cards:
            if not card.is_face_up():
                card.flip()
    
    def compute_bj_count(self):
        """ Compute the blackjack count of the cards in a hand, taking into
        account the value for an Ace as either 1 or 11, depending on the total
        count of the hand
        """
        count = sum(card.get_bj_value() for card in self.cards if card.is_face_up())
        
        if self.contains("Ace"):
            #hand contains an ace
            if count > 21:
                #count ace as 1
                count -= 10
        
        return count
                
        return sum(card.get_bj_value() for card in self.cards)
    
    def is_blackjack(self):
        """check if the count of a hand is 21 """
        return self.compute_bj_count() == 21
    
    def is_bust(self):
        """check if the count of a hand is over 21 """
        return self.compute_bj_count() > 21
    
    def contains(self, rank):
        """ check if the hand contains a certain rank"""
        return any(card.get_rank() == rank for card in self.cards)
        
#======================== Functions ===========================================

def bet_input(player):
    while True:
        try:
            bet = int(raw_input("Please place your bet: "))
        except ValueError:
            print "Sorry, please enter a valid bet"
            continue
        
        if bet > player1.get_balance():
            print "Sorry, the bet is larger than your balance, try again"
            continue
        else:
            break
        
    return bet



def hit_input(player):
    """Let the player decide to hit until stand, blackjack or bust """
    
    choice = raw_input("Do you want to hit (h) or stand (s)? h/s ")
    
    if choice.lower().startswith("h"):
        return True
    else:
        return False
                
def player_turn(deck, player, dealer):
    """
    the player's turn, player must choose stand or hit repeatedly until 
    chooses stand or busts
    If the player stands, return True. If he busts, return False
    """
    
    print ">>>>>>>> %s's turn <<<<<<<<" %(player)
    while hit_input(player1):
        #player wants to hit
        dealer.deal_cards(player1, deck, 1)
        print
        print "Player 1's hand: "
        player1.show_hand()
        print 
        
        #check for bust
        if player1.is_bust():
            #player looses
            print "Player 1 is bust"
            print
            return False
    
    return True

def dealer_turn(deck, player, dealer):
    """
    The dealer's turn. Dealer must hit until he has a count >= 17 or he
    is bust. 
    If the dealer stands, return True. If he busts, return False
    """
    
    print ">>>>>>>> Dealer's turn <<<<<<<<"
    
    #turn all cards face up
    dealer.open_hand()
    
    print "Dealer's hand: "
    dealer.show_hand()
    print 
    
    while dealer.should_hit():
        raw_input("Dealer must hit. Press enter to continue...")
        dealer.deal_cards(dealer, deck, 1)
        print
        print "Dealer's hand: "
        dealer.show_hand()
        print
        
        if dealer.is_bust():
            print "Dealer is bust"
            print
            return False
    
    print "Dealer must stand"     
    print
    return True

def payout_on_natural(dealer, player):
    
    if player.has_blackjack():
        if dealer.has_blackjack():
            # the dealer also has a natural
            print "Two naturals, it's a standoff! Dealer returns bet."
            # return the player's bet
            dealer.pay_out(player, "stand_off")
            print "%s has %d dollar" %(player, player.get_balance())
        else:
            print "%s has won, dealer pays out 1.5 times the bet." %(player)
            # dealer pays 1.5 times the player's bet
            dealer.pay_out(player, "natural")
            print "%s has %d dollar" %(player, player.get_balance())
    else:
        print "Dealer has blackjack, %s has lost! Dealer collects bet."
            
def payout_on_counts(dealer, player):
    """determine who has more points. If the dealer has more points, return 
    True, else return False"""
    dealer_count = dealer.get_count()
    player_count = player.get_count()
    #dealer stands
    if dealer_count > player_count:
        #player has lost
        print "%s has lost! Dealer collects bet." %(player)
        dealer.collect_bet(player1)
        print "%s has %d dollar." %(player, player.get_balance())
    elif dealer_count == player_count:
        print "It's a standoff! Dealer returns bet."
        dealer.pay_out(player1, "standoff")
        print "%s has %d dollar." %(player, player.get_balance())
    else:
        print "%s has won! Dealer pays out bet." %(player)
        dealer.pay_out(player1, "standard")
        print "%s has %d dollar." %(player, player.get_balance())
        

def rematch_input(player):
    if player.get_balance > 0:
        rematch = raw_input("Do you want to play another round? y/n ")
        if rematch.lower().startswith("y"):
            return True
    
    return False
    
def reset_table(deck, player, dealer):
    player.reset_hand()
    dealer.reset_hand()
    #check the deck size
    if len(deck) < 10:
        #reshuffle deck
        print "Reshuffled the deck"
        deck.new_deck()
        deck.shuffle()
###############################################################################    
#                               Main program                                  #
###############################################################################

#TODO build in check for the size of the deck, when do you need to reshuffle
#
#TODO rebuild deck when it's length is X cards
#TODO dealer has face down card 

#intialize a randomly shuffled deck of cards
deck = Deck()
deck.shuffle()

#intialize player(s) and dealer
player1 = Player("Player1", 100)
dealer = Dealer("Dealer")

print "Let's start! Player 1 has 100 dollar."

# game loop
running = True
while running:
    #player places bet
    player1.place_bet(bet_input(player1))
    
    # dealer deals two cards to player face up and two to himself, 
    dealer.deal_cards(player1, deck, 2) 
    dealer.deal_cards(dealer, deck, 2, 1)
    
    
    #print the cards
    print ">>>>>>>> The dealer deals the cards <<<<<<<< "
    print
    print "Player 1 received: "
    player1.show_hand()
    print
     #if dealer has 10 or ace, turn face down card up
    if dealer.first_card_10_or_ace():
        dealer.open_hand()
    
    print "Dealer received:"
    dealer.show_hand()
    print
    
    
        
    
    # check for blackjack player, 
    # for natural, otherwise wait until it's the dealers turn to play
    # if dealer has a natural, but player has not: dealer collects bet
    if player1.has_blackjack() or dealer.has_blackjack():
        payout_on_natural(dealer, player1)
   
            
    player_stands = player_turn(deck, player1, dealer)
    
    
    if not player_stands:
        #player busts
        dealer.collect_bet(player1)
        print "Player 1 has %d dollar" %(player1.get_balance())
        if rematch_input(player1):
            reset_table(deck, player1, dealer)
            continue
        else:
            running = False
            continue
      
        
    #the player stands, so now it is the dealers turn
    #TODO: if the player has 21 then it is not necessary to continue!
    dealer_stands = dealer_turn(deck, player1, dealer)
   
    if dealer_stands:
        #both player and dealer stand, compare counts and payout or collect
        payout_on_counts(dealer, player1)
    else:
        #dealer busts
        print "Player1 has won! Dealer pays out bet."
        dealer.pay_out(player1, "standard")
        print "Player 1 has %d dollar." %(player1.get_balance())
        
    
    if rematch_input(player1):
        reset_table(deck, player1, dealer)
        continue
    else:
        running = False
        continue
      
       
 
        
                
    
        
   











