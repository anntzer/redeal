"""Deal's example 1, with smartstacking:

North is 44 in the majors, short in a minor, and has 11-15HCP.
"""

from redeal import *

Roman = Shape("44(41)") + Shape("44(50)")
predeal = {"N": SmartStack(Roman, Evaluator(4, 3, 2, 1), range(11, 16))}
