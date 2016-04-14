Redeal: a reimplementation of Thomas Andrews' Deal in Python.
=============================================================

Thomas Andrew's Deal is a deal generator: it outputs deals satisfying whatever
conditions you specify -- deals with a double void, deals with a strong 2♣
opener opposite a yarborough, etc.  Using Bo Haglund's double dummy solver, it
can even solve the hands it has generated for you. Unfortunately, I have never
really liked the language Deal uses for scripting: Tcl.  Redeal is thus my
rewrite of Deal using another language: Python.

Redeal runs under Python 2.7 or higher.  See the `examples/` folder for some
example simulations.

A double-dummy solver function is also available through Bo Haglund's DDS
2.8.1, which is distributed with Redeal as a git submodule.  For Unix
systems, run `git submodule init && git submodule update` to fetch the
sources, then DDS will be built upon package installation (`./setup.py
build` or `./setup.py install`).  Note that this requires the `libgomp`
package.  You can also download the compiled shared objects from [Bo Haglund's
website](`http://privat.bahnhof.se/wb758135/bridge/dll.html`).  For Windows,
the DDS DLLs are distributed together with Redeal (the 64-bit DLL only works
for Python 3.5 or higher, let me know if you can help me fix this).  In any
case, if you cannot compile the DDS library, Redeal will work fine but the
`dd_tricks`, `dd_score` and `dd_all_tricks` methods will be unavailable.

Installation
------------

Download everything, open a terminal (a.k.a. Command Prompt in Windows), `cd`
to the directory where you downloaded the code and run `./setup.py install` (if
using a Unix system, you will need to either use `sudo`, or pass the `--user`
flag, too).  This will create two executable, `redeal` and `redeal-gui`.

Note that you do not actually need to install anything, if you do not wish
to.  Instead, you can also `cd` to the folder containing this `README`, build
`dds` (`./setup.py build`) and run `python -m redeal` instead of `redeal`, and
`python -m redeal --gui` instead of `redeal-gui`.

Now, run `redeal --help` (or `python -m redeal` if you did not install
`redeal`), or `redeal` to get a few hands, or `redeal examples/deal1.py` for
an example simulation.  In the `examples` folder, `./run_all_examples.sh` (or
`run_all_examples.bat` on Windows) will go through all the examples.

A note on the GUI
-----------------

Redeal provides a GUI, `redeal-gui`, if you are not comfortable using the
command line.  Some GUI-specific information is scattered in the tutorial so
read on!

An introductory tutorial
------------------------

All these examples come from Deal's documentation.

### Dealing hands

Run `redeal` at the command line to deal 10 hands, or `redeal -n N` to deal N
hands.

    $ redeal -n2
    ♠AQ53♡QJ9♢K963♣T9 ♠K♡AK853♢AQ87♣A42 ♠976♡7642♢T2♣KJ73 ♠JT842♡T♢J54♣Q865
    ♠T7♡J862♢QT4♣8752 ♠Q93♡T95♢A32♣KQ94 ♠K854♡AK7♢KJ87♣T3 ♠AJ62♡Q43♢965♣AJ6
    Tries: 2

Note that if your terminal does not support UTF-8 (e.g. Windows' Command
Prompt, or possibly Mac's Terminal.app), or if using Python 2, suit symbols
will be replaced by letters -- but the rest should work fine.

Here, the number of tries is the same as the number of hands, as any hand is
accepted.  This may not be the case in more complex cases.

Using the GUI, just keep click `Run` to go!  The number of requested deals can
be set at the top of the window.

### Stacking a hand

Would you open 2 or 3♡ with ♠-♡KQJT62♢T9876♣84?  Well, let's deal a couple of
hands to see how this would fare.

    $ redeal -S '- KQJT62 T9876 84'
    ♠AT982♡854♢J42♣KT ♠KQ7♡A973♢AK5♣AQJ ♠♡KQJT62♢T9876♣84 ♠J6543♡♢Q3♣976532
    ♠85♡854♢K4♣JT9752 ♠K97643♡A97♢A♣KQ6 ♠♡KQJT62♢T9876♣84 ♠AQJT2♡3♢QJ532♣A3
    ♠94♡97♢KJ42♣QJ972 ♠KJ852♡A85♢AQ3♣K5 ♠♡KQJT62♢T9876♣84 ♠AQT763♡43♢5♣AT63
    ♠KJT963♡A954♢K4♣2 ♠AQ82♡7♢5♣AKJT753 ♠♡KQJT62♢T9876♣84 ♠754♡83♢AQJ32♣Q96
    ♠984♡93♢AJ543♣AK7 ♠AJ52♡A84♢KQ♣JT96 ♠♡KQJT62♢T9876♣84 ♠KQT763♡75♢2♣Q532
    ♠J974♡53♢QJ43♣T62 ♠AKQ852♡A97♢♣J975 ♠♡KQJT62♢T9876♣84 ♠T63♡84♢AK52♣AKQ3
    ♠742♡73♢AQ♣AK9763 ♠KJT♡A95♢J542♣J52 ♠♡KQJT62♢T9876♣84 ♠AQ98653♡84♢K3♣QT
    ♠Q82♡A9♢A42♣AT732 ♠AJ754♡85♢KJ5♣Q95 ♠♡KQJT62♢T9876♣84 ♠KT963♡743♢Q3♣KJ6
    ♠QJT543♡8♢AJ3♣Q53 ♠K876♡A9743♢K5♣JT ♠♡KQJT62♢T9876♣84 ♠A92♡5♢Q42♣AK9762
    ♠AQJ8432♡4♢AQ♣KT5 ♠KT96♡A98♢32♣AJ76 ♠♡KQJT62♢T9876♣84 ♠75♡753♢KJ54♣Q932
    Tries: 10

There are also `-N`, `-E` and `-W` options, with the expected meanings.  Note
that you do not have to indicate 13 cards for a hand, but you always have to
specify the four suits.  For example, you can select hands where North holds
the heart ace with `redeal -S '- A - -'`.

Using the GUI, input the hands (using the same format) in the boxes labeled
"North", "South", "East" and "West".

### Formatting output

The default output is compact, but not very friendly.  What about more classic
diagrams?  The `-l` flag (or the GUI's "long output for diagrams" option) is
there for that!

    $ redeal -l -n1

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
For now, we will use a crude definition for an opening 1♠ call -- we will
require North to have 5 or more spades and 12 or more points.

Here is the script we write, to a file we'll call `onespade.py`, or in the
`accept` box of the GUI:

    def accept(deal):
        if len(deal.north.spades) >= 5 and deal.north.hcp >= 12:
            return True

and run it as follows:

    $ redeal examples/onespade.py # put the path to onespade.py
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

In our case, `deal.north` represents North's hand, `deal.north.spades` is a
list of North's spade holding, and `deal.north.hcp` is North's number of HCP.
If the conditions are satisfied, we return `True`.  This prints the hand and
increments the counter of accepted hands.

Redeal gives more information about its progress when given the `-v` flag (or
when the "be verbose" box of the GUI is ticked):

    $ redeal -v examples/onespade.py
    Using default for predeal.
    Using default for initial.
    Using default for do.
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
(which accepts all hands), but the one you defined, that is used.  As one can
see, there are in total, four functions that can be overriden:

- `initial` (taking no argument) is called when the simulation begins
  (defaults to doing nothing)
- `accept` (taking a `deal` argument) should return True or False depending
  on whether the deal is accepted -- defaults to always True,
- `do` (taking a `deal` argument) is called on each accepted deal --
  defaults to printing the deal,
- `final` (taking a `n_tries` argument) is called when the simulation ends
  (defaults to printing the number of tries).

One can also give the `accept` function, as the body of a function taking a
`deal` argument, at the command line:

    $ ./redeal.py --accept 'return len(deal.north.spades) >= 5 and \
        deal.north.hcp >= 12'
    ♠AKJT7♡85♢865♣KQ7 ♠852♡A74♢AQT42♣86 ♠963♡KJ3♢J973♣AT4 ♠Q4♡QT962♢K♣J9532
    ♠AKT86♡AJ76♢64♣42 ♠J954♡T♢KT752♣KT5 ♠3♡KQ853♢A983♣Q76 ♠Q72♡942♢QJ♣AJ983
    ♠AQ753♡A96♢A♣AT43 ♠KJT6♡KQ83♢Q753♣8 ♠9♡JT75♢KT42♣KQJ7 ♠842♡42♢J986♣9652
    ♠A98543♡63♢KQ♣AQ9 ♠J2♡AJT2♢J976♣J63 ♠QT6♡K9874♢T43♣K8 ♠K7♡Q5♢A852♣T7542
    ♠AK9642♡JT♢J9♣A42 ♠75♡A732♢AKQ84♣Q3 ♠T3♡K54♢T653♣KJT6 ♠QJ8♡Q986♢72♣9875
    ♠AK832♡3♢32♣AKQT2 ♠964♡J6♢AKJ5♣8765 ♠J7♡AK8542♢6♣J943 ♠QT5♡QT97♢QT9874♣
    ♠AQ432♡♢KJT43♣Q74 ♠J985♡9765♢A862♣T ♠6♡AKQJ82♢Q7♣AJ32 ♠KT7♡T43♢95♣K9865
    ♠AJT83♡AJ8♢82♣Q75 ♠Q64♡Q975♢J76♣KJ2 ♠75♡KT4♢KT93♣T943 ♠K92♡632♢AQ54♣A86
    ♠AJ652♡J2♢A9♣Q953 ♠KQ93♡AKT6♢KQ2♣84 ♠T87♡874♢873♣AT72 ♠4♡Q953♢JT654♣KJ6
    ♠KQJT9♡98♢KT♣K962 ♠♡J65432♢763♣AJ83 ♠A8652♡AQ7♢A8♣T54 ♠743♡KT♢QJ9542♣Q7
    Tries: 203


### Predealing and scripting

Your partner opens 1♠ and you hold ♠-♡96532♢A864♣T962... do you pass or bid
a forcing NT?  Let's generate a few hands so that we can see how we would fare.

    $ redeal -S '- 96532 A864 T962' examples/onespade.py
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

Again, one can also give the `accept` function at the command line.

Or, one can indicate the predealt cards ("stacked", in Deal jargon) in the
script, in the `predeal` variable:

    from redeal import * # this is "reasonably" safe

    predeal = {"S": H("- 96532 A864 T962")} # H is a hand constructor.

    def accept(deal):
        if len(deal.north.spades) >= 5 and deal.north.hcp >= 12:
            return True

Note that the predealing occurs outside of the `accept` function.  Also, the
`redeal` module has to be imported only for scripts in their own files; this is
done implicitely for the GUI and for functions given at the command line.

### Shape

Hands also have a `shape` attribute, which returns a list of the length in each
suit.  This can be queried directly, or using `Shape` objects, which are very
efficient:

    from redeal import *

    def accept(deal):
        return balanced(deal.north)

`balanced` is defined in `redeal.py` as

    balanced = Shape("(4333)") + Shape("(4432)") + Shape("(5332)")

where the parentheses have the usual meaning.  `semibalanced` is available as
well, and one can define other shapes, possibly using `x` as a generic
placeholder:

    major_two_suited = Shape("(54)xx") - Shape("(54)(40)")

### Vector additive functions

Quite a few hand evaluation techniques (HCP, controls, suit quality) look at
one suit at a time, and attribute some value to each card.  Just like `deal`,
`redeal` provides `Evaluator` for creating such evaluation functions:

    from redeal import *

    hcp = Evaluator(4, 3, 2, 1)
    controls = Evaluator(2, 1)
    top3 = Evaluator(1, 1, 1)

Now you can test the quality of a suit with, for example,
`top3(deal.north.spades) >= 2` (this may be relevant when generating weak two
hands).

### Smartstacking

For some rare hand types, Deal and Redeal provide an alternative hand dealing
technique: smartstacking.  Smartstacking works for only one of the four seats,
and can only take two sorts of constraints: a Shape object, and bounds on the
total value of a vector additive function (i.e. summed over the four suits).
For example, the following example finds hands where North is 4-4 in the major,
has a short minor and 11-15HCP.

    from redeal import *

    Roman = Shape("44(41)") + Shape("44(50)")
    predeal = {"N": SmartStack(Roman, (11 <= Evaluator(4, 3, 2, 1)) <= 15)}
    # Note the use of parentheses, which is *required*.

When smartstacking is used, Redeal starts by computing the relative
probabilities that each holding appears in a hand that satisfies the given
condition, which takes some time.  This then allows it to generate deals very
quickly, much faster than by generating random deals and checking whether they
pass an `accept` function.  For the given example, as long as one requests
a couple of dozen of hands, smartstacking is faster than direct dealing.

Smartstacking will take into account other (normally) predealt hands, and an
`accept` function can still be used, e.g. to still throw away some of the
hands.  See `examples/deal_gambling.py` for a complete example.

Finally, please note that smartstacking is only available for scripts in their
own files, not at the command line nor in the GUI.

// vim: fileencoding=utf-8

### NOTE* Mac OS X users zone:

First reinstall gcc: brew reinstall gcc --without-multilib
Next you have do change couple of stuff, when you clone repo with git clone --recursive git@github.com:anntzer/redeal.git you need to go and change some Makefile in dds/src (since they are not supporting .so libs on mac, it says in their README.md).
Go to dds/src/Makefiles/Makefile_Mac_gcc:

- on line 53 change STATIC_LIB = lib$(DLLBASE).a --> STATIC_LIB = lib$(DLLBASE).so
- then on line 85 change ar rcs $(STATIC_LIB) $(O_FILES) --> g++ -dynamiclib -o $(STATIC_LIB) $(O_FILES) -v
