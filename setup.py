import sys

if sys.version_info <= (3, 6):
    sys.exit("Python>=3.6 is required, but your version is:\n%s" % sys.version)

import setupext

setupext.main()
