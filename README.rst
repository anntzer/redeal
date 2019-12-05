======
Redeal
======

-----------------------------------------------------
A reimplementation of Thomas Andrews' Deal in Python.
-----------------------------------------------------

.. contents:: :local:

Thomas Andrew's Deal is a deal generator: it outputs deals satisfying whatever
conditions you specify -- deals with a double void, deals with a strong 2♣
opener opposite a yarborough, etc.  Using Bo Haglund's double dummy solver, it
can even solve the hands it has generated for you. Unfortunately, I have never
really liked the language Deal uses for scripting: Tcl.  Redeal is thus my
rewrite of Deal using another language: Python.

Redeal runs under Python 3.6 or higher.  See the ``examples/`` directory for
some example simulations.

A double-dummy solver function is also available through Bo Haglund's DDS
2.9.0 (slightly patched at build time), which is distributed with Redeal as
a git submodule.  Note that this requires the ``libgomp`` package.  You can
also download the compiled shared objects from `Bo Haglund's website`__.
For Windows, the DDS DLLs are distributed together with Redeal.  In any
case, if you cannot compile the DDS library, Redeal will work fine but the
``dd_tricks``, ``dd_score`` and ``dd_all_tricks`` methods will be unavailable.

__ http://privat.bahnhof.se/wb758135/bridge/dll.html

Installation
============

On a Unix system, do **not** download the ``.zip`` or ``.tar.gz`` releases.
They do not contain the DDS library.  The recommended way to install the
package is directly from GitHub,

.. code:: sh

    $ python -mpip install --user --upgrade git+https://github.com/anntzer/redeal

On Windows **only**, you can also download the ``.zip`` archive (from master,
not from the releases), and run, from the directory containing the archive,
``python -mpip install --user --upgrade redeal-master.zip`` (or whatever name
it has).

Directly running ``setup.py`` is **not** supported in either case.

Now, run ``redeal --help``, or ``redeal`` to get a few hands, or ``redeal
examples/deal1.py`` for an example simulation.  In the ``examples``
directory (which you can extract from the zip archive), ``python
__run_all_examples__.py`` will go through all the examples.

A note on the GUI
=================

Redeal provides a GUI, ``redeal-gui``, if you are not comfortable using the
command line.  Some GUI-specific information is scattered in the tutorial so
read on!

An introductory tutorial
========================

All these examples come from Deal's documentation.

Dealing hands
-------------

Run ``redeal`` at the command line to deal 10 hands, or ``redeal -n N`` to deal
``N`` hands.

.. code:: sh

    $ redeal -n2
    ♠AQ53♡QJ9♢K963♣T9 ♠K♡AK853♢AQ87♣A42 ♠976♡7642♢T2♣KJ73 ♠JT842♡T♢J54♣Q865
    ♠T7♡J862♢QT4♣8752 ♠Q93♡T95♢A32♣KQ94 ♠K854♡AK7♢KJ87♣T3 ♠AJ62♡Q43♢965♣AJ6
    Tries: 2

Note that if your terminal does not support UTF-8 (e.g. Windows' Command
Prompt, or possibly Mac's Terminal.app), suit symbols will be replaced by
letters -- but the rest should work fine.

Here, the number of tries is the same as the number of hands, as any hand is
accepted.  This may not be the case in more complex cases.

Using the GUI, just keep click ``Run`` to go!  The number of requested deals
can be set at the top of the window.

Stacking a hand
---------------

Would you open 2 or 3♡ with ♠-♡KQJT62♢T9876♣84?  Well, let's deal a couple of
hands to see how this would fare.

.. code:: sh

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

There are also ``-N``, ``-E`` and ``-W`` options, with the expected meanings.
Note that you do not have to indicate 13 cards for a hand, but you always have
to specify the four suits.  For example, you can select hands where North holds
the heart ace with ``redeal -S '- A - -'``.

Using the GUI, input the hands (using the same format) in the boxes labeled
"North", "South", "East" and "West".

Formatting output
-----------------

The default output is compact, but not very friendly.  What about more classic
diagrams?  The ``--format=long`` flag (or the GUI's "long output for diagrams"
option) is there for that!

.. code:: sh

    $ redeal --format=long -n1

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

Our first script
----------------

Let's say we want a selection of deals in which north holds a one spade opener.
For now, we will use a crude definition for an opening 1♠ call -- we will
require North to have 5 or more spades and 12 or more points.

Here is the script we write, to a file we'll call ``onespade.py``, or in the
``accept`` box of the GUI:

.. code:: python

    def accept(deal):
        if len(deal.north.spades) >= 5 and deal.north.hcp >= 12:
            return True

and run it as follows:

.. code:: sh

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

The ``accept`` function is called after each deal is dealt.  It can either
return ``True`` (or any Python-truthy object), if the deal satisfies our
conditions, or ``False`` (or any Python-falsey object) otherwise -- in which
case it is not counted towards the goal of 10 deals.  Note that at the end,
redeal also gives us the total number of hands it had to deal in order to get
10 accepted hands.

In our case, ``deal.north`` represents North's hand, ``deal.north.spades`` is a
list of North's spade holding, and ``deal.north.hcp`` is North's number of HCP.
If the conditions are satisfied, we return ``True``.  This prints the hand and
increments the counter of accepted hands.

There are in total, four functions that can be overridden:

- ``initial`` (taking no argument) is called when the simulation begins
  (defaults to doing nothing)
- ``accept`` (taking a ``deal`` argument) should return True or False depending
  on whether the deal is accepted -- defaults to always True,
- ``do`` (taking a ``deal`` argument) is called on each accepted deal --
  defaults to printing the deal,
- ``final`` (taking a ``n_tries`` argument) is called when the simulation ends
  (defaults to printing the number of tries).

One can also give the ``accept`` function, as the body of a function taking a
``deal`` argument, at the command line:

.. code:: sh

    $ redeal --accept 'return len(deal.north.spades) >= 5 and deal.north.hcp >= 12'
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


Predealing and scripting
------------------------

Your partner opens 1♠ and you hold ♠-♡96532♢A864♣T962... do you pass or bid
a forcing NT?  Let's generate a few hands so that we can see how we would fare.

.. code:: sh

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

Again, one can also give the ``accept`` function at the command line.

Or, one can indicate the predealt cards ("stacked", in Deal jargon) in the
script, in the ``predeal`` variable:

.. code:: python

   from redeal import * # this is "reasonably" safe

   predeal = {"S": H("- 96532 A864 T962")} # H is a hand constructor.

   def accept(deal):
      if len(deal.north.spades) >= 5 and deal.north.hcp >= 12:
         return True

Note that the predealing occurs outside of the ``accept`` function.  Also, the
``redeal`` module has to be imported only for scripts in their own files; this
is done implicitely for the GUI and for functions given at the command line.

Shape
-----

Hands also have a ``shape`` attribute, which returns a list of the length in
each suit.  This can be queried directly, or using ``Shape`` objects, which are
very efficient:

.. code:: python

   from redeal import *

   def accept(deal):
      return balanced(deal.north)

``balanced`` is defined in ``redeal.py`` as

.. code:: python

   balanced = Shape("(4333)") + Shape("(4432)") + Shape("(5332)")

where the parentheses have the usual meaning.  ``semibalanced`` is available as
well, and one can define other shapes, possibly using ``x`` as a generic
placeholder:

.. code:: python

   major_two_suited = Shape("(54)xx") - Shape("(54)(40)")

Vector additive functions
-------------------------

Quite a few hand evaluation techniques (HCP, controls, suit quality) look at
one suit at a time, and attribute some value to each card.  Just like ``deal``,
``redeal`` provides ``Evaluator`` for creating such evaluation functions:

.. code:: python

   from redeal import *

   hcp = Evaluator(4, 3, 2, 1)
   controls = Evaluator(2, 1)
   top3 = Evaluator(1, 1, 1)

Now you can test the quality of a suit with, for example,
``top3(deal.north.spades) >= 2`` (this may be relevant when generating weak two
hands).

Smartstacking
-------------

Rare hand types (say, 22 to 24 balanced) can be annoying to work with, as
``redeal`` needs to generate a lot of hands before finding any of them.  You
can pass the ``-v`` flag (not available from the GUI) to add some progress
information to the output.

For some rare hand types, Deal and Redeal provide an alternative, faster hand
dealing technique: smartstacking.  Smartstacking works for only one of the
four seats, and can only take two sorts of constraints: a Shape object, and
bounds on the total value of a vector additive function (i.e. summed over the
four suits).  For example, the following example finds hands where North is
4-4 in the major, has a short minor and 11-15HCP.

.. code:: python

   from redeal import *

   Roman = Shape("44(41)") + Shape("44(50)")
   predeal = {"N": SmartStack(Roman, Evaluator(4, 3, 2, 1), range(11, 16))}

When smartstacking is used, Redeal starts by computing the relative
probabilities that each holding appears in a hand that satisfies the given
condition, which takes some time.  This then allows it to generate deals very
quickly, much faster than by generating random deals and checking whether they
pass an ``accept`` function.  For the given example, as long as one requests
a couple of dozen of hands, smartstacking is faster than direct dealing.

Smartstacking will take into account other (normally) predealt hands, and an
``accept`` function can still be used, e.g. to still throw away some of the
hands.  See ``examples/deal_gambling.py`` for a complete example.

Finally, please note that smartstacking is only available for scripts in their
own files, not at the command line nor in the GUI.

External links
==============

Some articles written by users showcasing the use of Redeal:

- `A Simulation Tutorial for Better Decisionmaking at Bridge.`__

__ http://datadaydreams.com/posts/a-simulation-tutorial-for-better-decisionmaking-at-bridge/

Generating deals using Python
=============================

Deals can also be generated programmatically from Python, instead of using the
``redeal`` program. Here's an example:

.. code:: python

   from redeal import *

   def accept(deal):
       return deal.north.hcp >= 18

   dealer = Deal.prepare()

   # A random deal is generated
   deal1 = dealer()

   # Generate another one, using our accept function above
   deal2 = dealer(accept)

You may also use predealing and SmartStacking, as an argument to
``Deal.prepare``:

.. code:: python

   from redeal import *

   def accept(deal):
       return deal.north.hcp >= 15

   dealer = Deal.prepare({'S': 'K83 AK83 - QJT972'})
   deal = dealer(accept)

.. vim: set fileencoding=utf-8:
