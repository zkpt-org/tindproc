#!/usr/local/bin/python
import IPython.core.ipapi, os, sys, json, copy, itertools
from datetime import datetime

dirname = os.path.dirname(os.path.abspath(__file__))
os.chdir(dirname)
sys.path.append('../')
from das.das import Das
from lib.db import PgSQL
from lib.helpers import timewindow, chronic, employers
from functions import home

# set up ipython development environment
ipython = IPython.core.ipapi.get()
ipython.magic('%load_ext autoreload')
ipython.magic('%autoreload 2')

# start timer for performance metrics
timer = datetime.now()
sql = PgSQL()
# check if the authentication step has been performed
if 'PGT' not in os.environ:
    das = Das()
    das.auth()
    os.environ['PGT'] = das.PGT
else:
    das = Das()
    das.PGT = os.environ['PGT']

win = timewindow(das)
# emp = employers(das, win)
sys.exit()

cuts = [
['ALL','XYZ private ltd','ABC corporation'], # client
['ALL'], # office
['ALL'], # level
['ALL', 'Male', 'Female'], # gender
['ALL', '18-29', '30-39', '40-49', '50-59', '60-69', '70+'], # age group
['ALL'] + chronic(das, win) # conditions
]

cycles = 0
for cut in itertools.product(*cuts): cycles+=1

i = 0
for cut in itertools.product(*cuts):
    i+=1
    query = {
    "client"     : cut[0],
    "office"     : cut[1],
    "level"      : cut[2],
    "condition"  : cut[5],
    "gender"     : cut[3],
    "age"        : cut[4],
    "start_date" : win["reporting_from"],
    "end_date"   : win["reporting_to"]
    }
    insert = copy.deepcopy(query)
    insert.update({"data":"", "created":"NOW", "modified":"NOW"})

    # try:
        # if not sql.select(table='home_graph1', where=query):
        #     g1 = json.dumps(home.graph1(das, win))
        #     insert["data"] = str(g1)
        #     sql.insert(table='home_graph1', rows=[insert])
        #     
        # if not sql.select(table='home_graph2', where=query):
        #     g2 = json.dumps(home.graph2(das, win))
        #     insert["data"] = str(g2)
        #     sql.insert(table='home_graph2', rows=[insert])
        #     
        # if not sql.select(table='home_graph3', where=query):
        #     g3 = json.dumps(home.graph3(das, win))
        #     insert["data"] = str(g3) 
        #     sql.insert(table='home_graph3', rows=[insert])
        
    if not sql.select(table='home_graph4', where=query):
        g4 = json.dumps(home.graph4(das, win, query))
        insert["data"] = str(g4)
        print g4
        sql.insert(table='home_graph4', rows=[insert])

    # except Exception,e:
    #     print str(e)+"\n"
    #     with open("../errors.log", "a+") as f: f.write(str(e)+"\n")

    print str(i) + " of " + str(cycles) + "\n"
        
print "Executed in", str(datetime.now()-timer)[:-4] + "\a\n"