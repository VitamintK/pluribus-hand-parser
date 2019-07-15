# PLUR  ☮️ 🤩
from textwrap import wrap
from collections import namedtuple
import re

def read_directory():
    return

def read_file():
    return 

class Hands:
    pass

class Hand:
    
    def __init__(self, hand_text, session_number = None):
        self.session = session_number
        self.hand_text = hand_text
    def get_action_groups(action_string):
        number_of_actions = len([x for x in action_string if x in 'cfr'])
        action_strings = re.match("^{}$".format('([crf]\\d*)'*number_of_actions), action_string)
        return action_strings.groups()
    def _parse_register_action(self, player_seat, action_type, amount=None):
        # street  0: blind, 1: preflop, 2: postflop, 3: turn, 4: river
        # in case of call, no need to declare amount.  it will be automatically calculated.
        # for a raise, amount should be the total amount that player has put in pot this street (ie the value coming from raw logs)
        total_amount = None
        marginal_amount = None
        if action_type in ['sb', 'bb', 'b']:
            total_amount = amount - self._parse_max_money_in_pot_after_last_round
            self._parse_max_money_in_pot = max(self._parse_max_money_in_pot, amount)
            self._parse_money_in_pot[player_seat] = amount
        elif action_type in ['r']:
            marginal_amount = amount - self._parse_max_money_in_pot
            self._parse_max_money_in_pot = amount
            self._parse_money_in_pot[player_seat] = amount
            total_amount = amount - self._parse_max_money_in_pot_after_last_round
        elif action_type in ['ca']:
            prev_amount = self._parse_money_in_pot[player_seat]
            self._parse_money_in_pot[player_seat] = self._parse_max_money_in_pot
            marginal_amount = self._parse_max_money_in_pot - prev_amount
        elif action_type in ['ch']:
            pass
        self.actions[self._parse_cur_street].append(Action(self.player_ids[player_seat], action_type, total_amount, marginal_amount))

    def _parse_increment_street(self):
        if self._parse_cur_street != 0:
            self._parse_max_money_in_pot_after_last_round = self._parse_max_money_in_pot
        self._parse_cur_street += 1
        


    def parse(self):
        split = self.hand_text.split(':')
        if len(split) != 6:
            raise ValueError("hand_text for this Hand does not contain 6 parts: {}".format(hand_text))
        if split[0] != 'STATE':
            raise ValueError("hand_text for this Hand is not a single line of text starting with 'STATE:' {}".format(hand_text))

        state, hand_number, actions, cards, profit, player_ids = split
        self.hand_number = hand_number
        self.player_ids = player_ids.split('|')
        self.profits = [int(p) for p in profit.split('|')]

        cards_by_street = cards.split('/')
        actions_by_street = actions.split('/')
        self.player_hole_cards = [Cards(hole_cards) for hole_cards in cards_by_street[0].split('|')]
        self.community_cards_by_street = [Cards(community_cards) for community_cards in cards_by_street[1:]]
        
        # start build actions ###############################
        players_active = [1 for i in self.player_ids]
        self._parse_max_money_in_pot_after_last_round = 0
        self._parse_cur_street = 0
        self._parse_max_money_in_pot = 0
        self._parse_money_in_pot = [0 for i in self.player_ids]
        self.actions = [[] for i in range(len(actions_by_street)+1)]
        # self.money_in_pot_by_player_by_street = [[0 for i in self.player_ids] for j in actions_by_street]
        #blind:
        #actions_for_street = []
        # actions_for_street.append(Action(self.player_ids[0], 'sb', 50))
        # actions_for_street.append(Action(self.player_ids[1], 'bb', 100))
        self._parse_register_action(0, 'sb', 50)
        self._parse_register_action(1, 'bb', 100)
        # self.actions.append(actions_for_street)
        # preflop:
        cur_player = 2
        can_check = False
        # each street:
        for street in actions_by_street:
            self._parse_increment_street()
            actions_for_street = []
            actions_for_street_string = Hand.get_action_groups(street)
            for action in actions_for_street_string:
                while not players_active[cur_player]:
                    cur_player = (cur_player +1)%6
                action_type = action[0]
                amount = None
                if action_type == 'r':
                    amount = int(action[1:])
                    if can_check:
                        action_type = 'b'
                    else:
                        action_type = 'r'
                    can_check = False
                elif action_type == 'f':
                    players_active[cur_player] = 0
                elif action_type == 'c':
                    if can_check:
                        action_type = 'ch'
                    else:
                        action_type = 'ca'

                # actions_for_street.append(Action(self.player_ids[cur_player], action_type, amount))
                self._parse_register_action(cur_player, action_type, amount)
                cur_player = (cur_player + 1)%6
            # self.actions.append(actions_for_street)

            # non-preflop:
            can_check = True
            cur_player = 0
        self.pot = sum(x for x in self._parse_money_in_pot)
        # print(self.actions)
        # end build actions ##############

    def __str__(self):
        return self.hand_text



    def get_poker_stars_str(self):
        session = self.session if self.session else 0
        hh = ''
        hh += "PokerStars Hand #{}: Hold'em No Limit (50/100) - {} [{}]\n".format(1000*session + int(self.hand_number), '2017/08/08 23:16:30 MSK', '2017/08/08 16:16:30 ET')
        hh += "Table 'Pluribus Session {}-{}' 6-max (Play Money) Seat #6 is the button\n".format('TODO', self.hand_number)
        for seat, player_id in enumerate(self.player_ids):
            hh += "Seat {}: {} (10000 in chips)\n".format(seat+1, player_id)
        for action in self.actions[0]:
            hh += action.get_poker_stars_str() + '\n'
        hh += '*** HOLE CARDS ***\n'
        for player_id, hole_cards in zip(self.player_ids, self.player_hole_cards):
            hh += 'Dealt to {} {}\n'.format(player_id, hole_cards.get_poker_stars_str())
        for action in self.actions[1]:
            hh += action.get_poker_stars_str() + '\n'
        titles = ['FLOP', 'TURN', 'RIVER']
        community_cards_strs = []
        for street_no, community_cards in enumerate(self.community_cards_by_street):
            community_cards_strs.append(community_cards.get_poker_stars_str())
            hh += '*** {} *** {}\n'.format(titles[street_no], ' '.join(community_cards_strs))
            for action in self.actions[street_no+2]:
                hh += action.get_poker_stars_str() + '\n'
        if len(self.community_cards_by_street) == 3 and self.actions[-1][-1].action_type in ['ca', 'ch']:
            hh += "*** SHOWDOWN ***\n"
        for player_no, player_id in enumerate(self.player_ids):
            if self.profits[player_no] > 0:
                hh += "{} collected {} from pot\n".format(player_id, self.pot)
        hh += "*** SUMMARY ***\n"
        # the following calculation for total pot, or something similar should work, but the profits section seems incorrect as of now
        # issue filed at: https://twitter.com/010010110000110/status/1150209114733105152
        # hh += "Total pot {} | Rake 0\n".format(sum(x for x in self.profits if x > 0))
        hh += "Total pot {} | Rake 0\n".format(self.pot)
        hh += "Board {}".format(sum(self.community_cards_by_street, Cards('')).get_poker_stars_str())
        # for seat, player_id in enumerate(self.player_ids):
        #     hh += "Seat {}: {}"
        return hh

class Action(namedtuple('Action', ['player_id', 'action_type', 'amount', 'marginal_amount'], defaults=[None, None])):
    __slots__ = ()
    def get_poker_stars_str(self):
        action_type_to_string = {'b': 'bets', 'f': 'folds', 'ca': 'calls', 'ch': 'checks', 'r': 'raises', 'sb': 'posts small blind', 'bb': 'posts big blind'}
        if self.action_type == 'r':
            return "{}: {} {} to {}".format(self.player_id, action_type_to_string[self.action_type], self.marginal_amount, self.amount)
        elif self.action_type in ['sb', 'bb', 'b']:
            return "{}: {} {}".format(self.player_id, action_type_to_string[self.action_type], self.amount)
        elif self.action_type in ['ca']:
            return "{}: {} {}".format(self.player_id, action_type_to_string[self.action_type], self.marginal_amount)
        else:
            return "{}: {}".format(self.player_id, action_type_to_string[self.action_type])

class Cards:
    def __init__(self, cards_string):
        self.cards_string = cards_string
        cards = wrap(cards_string, 2)
        self.cards = [Card(card) for card in cards]
    def get_poker_stars_str(self):
        return '[{}]'.format(' '.join(str(card) for card in self.cards))
    def __add__(self, left):
        return Cards(self.cards_string+left.cards_string)
        
class Card:
    def __init__(self, card_string):
        self.card_string = card_string
        self.rank = Rank(card_string[0])
        self.suit = Suit(card_string[1])
    def __str__(self):
        return self.card_string
class Rank:
    def __init__(self, rank_string):
        self.rank_string = rank_string
class Suit:
    def __init__(self, suit_string):
        self.suit_string = suit_string

if __name__ == '__main__':
    h1 = 'STATE:102:ffr225cff/cr825f:KcJd|4dTc|8dTh|3h8s|8cQc|5h6h/As5cJs:-50|-100|0|0|-225|375:Budd|MrWhite|MrOrange|Hattori|MrBlue|Pluribus'
    h2 = 'STATE:82:fffr225fr1225c/r1850c/r4662c/r10000c:3h9s|KsAh|7c5c|5d4h|2hKd|Ad8d/7d2sAs/Qh/8h:-50|-10000|0|0|0|10050:MrBlue|Pluribus|Budd|MrWhite|MrOrange|Hattori'
    h3 = 'STATE:42:r200fcffc/cr650cf/cr3000f:8c6h|7hJs|AdJh|9s2h|TdTs|5c3s/QdKc9d/Ac:-50|-200|-650|0|900|0:Budd|MrWhite|MrOrange|Hattori|MrBlue|Pluribus'
    for hx in [h1,h2,h3]:
        h = Hand(hx)
        h.parse()
        print(h.get_poker_stars_str())
        print(h)