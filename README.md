# pluribus-hand-parser
Standalone parser for the hands that pluribus played

the raw data is available by downloading [Data File S1 here](https://science.sciencemag.org/content/suppl/2019/07/10/science.aay2400.DC1).

THIS API IS SUBJECT TO EXTREME CHANGE.  This is version -1.

# Usage

```
$ python3 -i plur.py
>>> h = Hand('STATE:42:r200fcffc/cr650cf/cr3000f:8c6h|7hJs|AdJh|9s2h|TdTs|5c3s/QdKc9d/Ac:-50|-200|-650|0|900|0:Budd|MrWhite|MrOrange|Hattori|MrBlue|Pluribus')
>>> h.parse()
>>> print(h.get_poker_stars_str())
PokerStars Hand #42: Hold'em No Limit (50/100) - 2017/08/08 23:16:30 MSK [2017/08/08 16:16:30 ET]
Table 'Pluribus Session TODO-42' 6-max (Play Money) Seat #6 is the button
Seat 1: Budd (10000 in chips)
Seat 2: MrWhite (10000 in chips)
Seat 3: MrOrange (10000 in chips)
Seat 4: Hattori (10000 in chips)
Seat 5: MrBlue (10000 in chips)
Seat 6: Pluribus (10000 in chips)
Budd: posts small blind 50
MrWhite: posts big blind 100
*** HOLE CARDS ***
Dealt to Budd [8c 6h]
Dealt to MrWhite [7h Js]
Dealt to MrOrange [Ad Jh]
Dealt to Hattori [9s 2h]
Dealt to MrBlue [Td Ts]
Dealt to Pluribus [5c 3s]
MrOrange: raises 100 to 200
Hattori: folds
MrBlue: calls 200
Pluribus: folds
Budd: folds
MrWhite: calls 100
*** FLOP *** [Qd Kc 9d]
MrWhite: checks
MrOrange: bets 450
MrBlue: calls 450
MrWhite: folds
*** TURN *** [Qd Kc 9d] [Ac]
MrOrange: checks
MrBlue: bets 2350
MrOrange: folds
MrBlue collected 3900 from pot
*** SUMMARY ***
Total pot 3900 | Rake 0
Board [Qd Kc 9d Ac]
```

# Updates and ongoing work

Sorry to those who have requested a version that works with Hold'em Manager - I'll get around to approving that pull request eventually.  It looks like Hold'em Manager doesn't like the "play money" designation and needs $ amount to function correctly.

# Discussion
[reddit post](https://www.reddit.com/r/poker/comments/cdhasb/download_all_10000_hands_that_pluribus_poker_ai/)
