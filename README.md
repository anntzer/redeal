Redeal: a reimplementation of Thomas Andrews' Deal in Python.
=============================================================

Redeal runs under Python 2.7 or higher.  See the `examples/` folder for some
example simulations.

A double-dummy solver function is available through Bo Haglund's DDS v.1.1.9
(the latest version I could find that can easily be built on Linux -- extracted
and slightly modified from the source of Thomas Andrews' Deal), but you will
need a C++ compiler.  If you have g++ and make, simply run `make` in the
dds-1.1.9 folder; otherwise use the compiler of your choice.  If you cannot
compile the DDS library, Redeal will work fine but the `solve_board` function
will be unavailable.

Run `./redeal.py --help`, or `./redeal.py` to get a few hands, or `./redeal.py
examples/deal1.py` for an example simulation.  `./run_all_examples.sh` will go
through all the examples.

An introductory tutorial
------------------------

All these examples come from Deal's documentation.

### Dealing hands

Run `./redeal.py` at the command line to deal 10 hands, or `./redeal.py -n N`
to deal N hands.

    $ ./redeal.py -n2
    ♠AQ53♡QJ9♢K963♣T9 ♠K♡AK853♢AQ87♣A42 ♠976♡7642♢T2♣KJ73 ♠JT842♡T♢J54♣Q865
    ♠T7♡J862♢QT4♣8752 ♠Q93♡T95♢A32♣KQ94 ♠K854♡AK7♢KJ87♣T3 ♠AJ62♡Q43♢965♣AJ6
    Tries: 2

Here, the number of tries is the same as the number of hands, as any hand is
accepted.  This may not be the case in more complex cases.

### Stacking a hand

Would you open 2 or 3♡ with ♠-♡KQJT62♢T9876♣84?  Well, let's deal a couple of
hands to see how this would fare.

    $ ./redeal.py -S"- KQJT62 T9876 84" -n25         
    ♠AT982♡854♢J42♣KT ♠KQ7♡A973♢AK5♣AQJ ♠♡KQJT62♢T9876♣84 ♠J6543♡♢Q3♣976532
    ♠85♡854♢K4♣JT9752 ♠K97643♡A97♢A♣KQ6 ♠♡KQJT62♢T9876♣84 ♠AQJT2♡3♢QJ532♣A3
    <... 23 other hands elided>

### Formatting output

The default output is compact, but not very friendly.  What about more classic
diagrams?  The `-l` flag is there for that!

    $ ./redeal.py -l -n1
           
           ♠
           ♡632
           ♢AKT92
           ♣K7652
                  
    ♠AJ85         ♠T962
    ♡KJ954        ♡7
    ♢QJ           ♢8763
    ♣QJ           ♣AT94
           
           ♠KQ743
           ♡AQT8
           ♢54
           ♣83

    Tries: 1

### Our first script

Let's say we want a selection of deals in which north holds a one spade opener.
For now, we will use a crude definition for an opening 1♠ call - we will
require north to have 5 or more spades and 12 or more points.

Here is the script we write (to a file we'll call onespade.py):

    def accept(deal):
        if len(deal.north.spades) >= 5 and deal.north.hcp >= 12:
            print(deal) # use print(unicode(deal)) if using Python2
            return True

and run it as follows:

    $ ./redeal.py examples/onespade.py # put the path to onespade.py
    ♠AJ854♡J986♢T♣AKJ ♠KQ96♡2♢KJ874♣T52 ♠T732♡AKQT43♢Q2♣3 ♠♡75♢A9653♣Q98764
    ♠AQ875♡T87♢A♣QJ84 ♠T943♡♢9752♣T9652 ♠J6♡AQJ9432♢J6♣A7 ♠K2♡K65♢KQT843♣K3
    ♠KQ9874♡J4♢J43♣KQ ♠J65♡A873♢2♣AJT87 ♠A2♡K65♢AT975♣652 ♠T3♡QT92♢KQ86♣943
    ♠QT6543♡A9♢KT♣K32 ♠72♡KT74♢A9♣QT754 ♠J98♡QJ865♢QJ8♣J8 ♠AK♡32♢765432♣A96
    ♠AT862♡KQJ♢Q65♣K2 ♠QJ953♡A832♢7♣A53 ♠4♡T765♢KT983♣Q87 ♠K7♡94♢AJ42♣JT964
    ♠KQ974♡A652♢9♣QJ3 ♠AJ5♡Q7♢KQ8♣A9872 ♠♡K84♢AT76543♣T64 ♠T8632♡JT93♢J2♣K5
    ♠AJ943♡Q♢AQJT♣JT9 ♠T52♡AJT♢K852♣AQ6 ♠KQ6♡K876532♢97♣2 ♠87♡94♢643♣K87543
    ♠KQT532♡KQ♢K♣KQ92 ♠8♡T5♢A864♣AT7654 ♠AJ76♡98643♢Q5♣83 ♠94♡AJ72♢JT9732♣J
    ♠AT9743♡Q7♢J♣AKT2 ♠8♡A932♢AKT7♣J963 ♠K62♡J5♢98653♣874 ♠QJ5♡KT864♢Q42♣Q5
    ♠KJ842♡K5♢94♣AK74 ♠53♡Q7♢762♣Q98653 ♠AQ96♡943♢JT85♣JT ♠T7♡AJT862♢AKQ3♣2
    Tries: 120

The `accept` function is called after each deal is dealt.  It can either return
`True` (or any Python-truthy object), if the deal satisfies our conditions, or
`False` (or any Python-falsey object) otherwise -- in which case it is not
counted towards the goal of 10 deals.  Note that at the end, redeal also gives
us the total number of hands it had to deal in order to get 10 accepted hands.

In our case, `deal.north` represents North's hand, `deal.north.spades` is
a list of North's spade holding, and `deal.north.hcp` is North's number of HCP.
If the conditions are satisfied, we print the hand and return `True`, which
increment the counter of accepted hands.

Redeal gives more information about its progress when given the `-v` flag:

    ± ./redeal.py -v examples/onespade.py
    Using default for initial.
    Using default for predeal.
    Using default for final.
    ♠KT8754♡5♢AKQ76♣J ♠QJ♡AQ94♢T542♣972 ♠9632♡JT32♢J8♣864 ♠A♡K876♢93♣AKQT53
    (hand #1, found after 9 tries)
    ♠KQT985♡Q8♢KJ6♣J9 ♠62♡♢AT985♣AQ7543 ♠J74♡9643♢72♣T862 ♠A3♡AKJT752♢Q43♣K
    (hand #2, found after 37 tries)
    ♠AK9874♡AJ♢K98♣K8 ♠T5♡T872♢AT43♣A92 ♠QJ♡Q965♢7652♣QJ7 ♠632♡K43♢QJ♣T6543
    (hand #3, found after 97 tries)
    ♠AKQJ7♡J8653♢♣KQJ ♠T53♡T42♢A7542♣32 ♠984♡Q97♢QT96♣AT5 ♠62♡AK♢KJ83♣98764
    (hand #4, found after 116 tries)
    ♠AQ643♡KQ5♢KJ72♣J ♠K9♡AJ94♢T94♣T652 ♠72♡73♢AQ3♣AKQ984 ♠JT85♡T862♢865♣73
    (hand #5, found after 130 tries)
    ♠AT972♡Q94♢Q♣KQJT ♠J43♡AK632♢85♣985 ♠K5♡J8♢9763♣A7432 ♠Q86♡T75♢AKJT42♣6
    (hand #6, found after 158 tries)
    ♠AQT74♡A2♢64♣KT43 ♠J65♡QT863♢Q95♣J5 ♠932♡K9♢KJ32♣A972 ♠K8♡J754♢AT87♣Q86
    (hand #7, found after 165 tries)
    ♠AQ984♡T4♢J97♣AK9 ♠653♡J86♢A43♣JT84 ♠J7♡AQ73♢KQT8♣Q52 ♠KT2♡K952♢652♣763
    (hand #8, found after 179 tries)
    ♠AKJ73♡74♢QJ72♣Q7 ♠Q♡9863♢T843♣AT92 ♠86542♡AT♢K965♣53 ♠T9♡KQJ52♢A♣KJ864
    (hand #9, found after 188 tries)
    ♠Q8752♡AJ♢AQJ53♣8 ♠J43♡K875♢T9♣AKJ3 ♠AT9♡Q943♢K74♣Q76 ♠K6♡T62♢862♣T9542
    (hand #10, found after 204 tries)
    Tries: 204

This is also a good way to check that it is not the default `accept` function
(which accepts all hands), but the one you defined, that is used.

### Predealing and scripting

Your partner opens 1♠ and you hold ♠-♡96532♢A864♣T962... do you pass or bid
a forcing NT?  Let's generate a few hands so that we can see how we would fare.

    $ ./redeal.py -S"- 96532 A864 T962" examples/onespade.py
    ♠A8643♡A8♢QT72♣Q8 ♠QT972♡Q♢K95♣K754 ♠♡96532♢A864♣T962 ♠KJ5♡KJT74♢J3♣AJ3
    ♠AQ864♡4♢KJT72♣QJ ♠JT7♡AJT8♢Q3♣A743 ♠♡96532♢A864♣T962 ♠K9532♡KQ7♢95♣K85
    ♠AQT765♡7♢J72♣KQ8 ♠K9832♡AKT♢K953♣5 ♠♡96532♢A864♣T962 ♠J4♡QJ84♢QT♣AJ743
    ♠AJ932♡74♢KQJ7♣KJ ♠KQT65♡AK8♢532♣A4 ♠♡96532♢A864♣T962 ♠874♡QJT♢T9♣Q8753
    ♠KJ986♡AJT8♢K♣K75 ♠AT73♡Q74♢Q732♣Q8 ♠♡96532♢A864♣T962 ♠Q542♡K♢JT95♣AJ43
    ♠QJ9732♡A♢QJ♣AQ87 ♠T865♡J87♢K97♣J54 ♠♡96532♢A864♣T962 ♠AK4♡KQT4♢T532♣K3
    ♠AKQJT732♡K8♢7♣85 ♠4♡AJ74♢K53♣AKQJ4 ♠♡96532♢A864♣T962 ♠9865♡QT♢QJT92♣73
    ♠AK653♡Q84♢QT5♣J3 ♠982♡AT♢KJ97♣AKQ5 ♠♡96532♢A864♣T962 ♠QJT74♡KJ7♢32♣874
    ♠AKJ98752♡7♢J5♣A3 ♠Q643♡AQJ4♢Q3♣K85 ♠♡96532♢A864♣T962 ♠T♡KT8♢KT972♣QJ74
    ♠KJ9863♡♢Q9♣AKJ73 ♠AT75♡QT874♢72♣85 ♠♡96532♢A864♣T962 ♠Q42♡AKJ♢KJT53♣Q4
    Tries: 31

There are also `-N`, `-E` and `-W` switches, with the expected meanings.

Or, one can indicate the predealt cards ("stacked", in Deal jargon) in the
script, in the `predeal` variable:

    from redeal import * # this is "reasonably" safe

    predeal = {"S": H("- 96532 A864 T962")} # H is a hand constructor.

    def accept(deal):
        if len(deal.north.spades) >= 5 and deal.north.hcp >= 12:
            print(deal) # use print(unicode(deal)) if using Python2
            return True

Note that the predealing occurs outside of the `accept` function.

### Shape

Hands also have a `shape` attribute, which returns a list of the length in each
suit.  This can be queried directly, or using `Shape` objects, which are very
efficient:

    from redeal import *

    def accept(deal):
        return deal.north.shape in Balanced

`Balanced` is defined in `redeal.py` as

    Balanced = Shape("(4333)") + Shape("(4432)") + Shape("(5332)")

where the parentheses have the usual meaning.  `SemiBalanced` is available as
well, and one can define other shapes, possibly using `x` as a generic
placeholder:

    MajorTwoSuit = Shape("(54)xx") - Shape("(54)(40)")

### Vector additive functions

Quite a few hand evaluation techniques (HCP, controls, suit quality) look at
one suit at a time, and attribute some value to each card.  Just like `deal`,
`redeal` provides `defvector` for creating such evaluation functions:

    from redeal import *

    hcp = defvector(4, 3, 2, 1)
    controls = defvector(2, 1)
    top3 = defvector(1, 1, 1)

Now you can test the quality of a suit with, for example,
`top3(deal.north.spades) >= 2` (this may be relevant when generating weak two
hands).
