#!/usr/local/bin/python
import IPython.core.ipapi, os, sys, json
from datetime import datetime
# import pandas as pd
# import numpy as np

dirname = os.path.dirname(os.path.abspath(__file__))
os.chdir(dirname)
sys.path.append('../')
from das.das import Das
from lib.db import PgSQL
from functions import home

# set up ipython development environment
ipython = IPython.core.ipapi.get()
ipython.magic('%load_ext autoreload')
ipython.magic('%autoreload 2')

# start timer for performance metrics
timer = datetime.now()

# check if the authentication step has been performed
if 'PGT' not in os.environ:
    das = Das()
    das.auth()
    os.environ['PGT'] = das.PGT
else:
    das = Das()
    das.PGT = os.environ['PGT']

query = {}
query["reportingFrom"]  = start = "2013-01-01"
query["reportingTo"]    = end   = "2013-12-31"
query["comparisonFrom"] = "2012-01-01"
query["comparisonTo"]   = "2012-12-31"

g4 = json.dumps(home.graph4(das, query))

# try:
#     rows=[{"start_date":"'"+start+"'", "end_date":"'"+end+"'", "data":"'"+str(g4)+"'", "created":"'NOW'", "modified":"'NOW'"}]
#     PgSQL().insert(table='home_graph4', rows=rows)
# except Exception,e:
#     print str(e)+"\n"
#     with open("../errors.log", "a+") as f: f.write(str(e)+"\n")

print "Executed in", str(datetime.now()-timer)[:-4] + "\a\n"