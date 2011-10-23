#log# Automatic Logger file. *** THIS MUST BE THE FIRST LINE ***
#log# DO NOT CHANGE THIS LINE OR THE TWO BELOW -* coding: UTF-8 *-
#log# opts = Struct({'__allownew': True, 'logfile': 'ipython_log.py'})
#log# args = []
#log# It is safe to make manual edits below here.
#log#-----------------------------------------------------------------------
_ip.system("ls -F ")
_ip.system("ls -F ")
_ip.magic("cd labs")
_ip.system("ls -F ")
_ip.magic("cd lab2")
_ip.system("ls -F ")
_ip.magic("cd src")
_ip.magic("clear ")
_ip.system("ls -F ")
_ip.magic("run compiler.py")
_ip.system("ls -F ")
_ip.magic("run compiler.py")
from pylibs
import sys
sys.path
from pybin
import pybin
import pylibs
from pylibs.data_structures import graph
#?graph
log
_ip.magic("logstart ")

g = graph.Graph()
#?g.add_node
g.add_node("s0", attr="NT")
g.add_node("s1, attr="NT")
g.add_node("s1", attr="NT")
g.add_node("s2", attr="T")
#?g.add_edge
g.add_edge("s0", "s1", "r")
g.add_edge("s1", "s2", "0123456789")
g.add_edge("s2", "s2", "0123456789")
g.nodes 
g.nodes()
g.get_neighbors("s2")
_ip.magic("logstop ")
