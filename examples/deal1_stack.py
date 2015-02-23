"""Deal's example 1, with smartstacking:

North is 44 in the majors, short in a minor, and has 11-15HCP.
"""

from redeal import *

Roman = Shape("44(41)") + Shape("44(50)")
predeal = {"N": SmartStack(Roman, (11 <= Evaluator(4, 3, 2, 1)) <= 15)}
