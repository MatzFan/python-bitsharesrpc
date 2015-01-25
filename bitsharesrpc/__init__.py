#from .client import client
import sys
if sys.version > '3' :
    from .client import client
else :
    from client import client
