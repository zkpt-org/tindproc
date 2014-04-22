import IPython.core.ipapi, os, sys #, time
from datetime import datetime
# sys.path.append('./')
from das.das import Das

ipython = IPython.core.ipapi.get()
ipython.magic('%load_ext autoreload')
ipython.magic('%autoreload 2')

timer = datetime.now()

if 'PGT' not in os.environ:
    das = Das()
    das.auth()
    os.environ['PGT'] = das.PGT
else:
    das = Das()
    das.PGT = os.environ['PGT']

# p = {"service" : "search", "table" : "ms"}
# p = {"service" : "search", "table" : "ms", "cohortId" : "74028_1396993055652_891847"}
p = {"service" : "search", "table" : "ms", 'query' : "{'and':[{'memberGender.eq':'F'}]}"}
# p = {"service" : "search", "table" : "ms", "page" : "1", "pageSize" : "10"}
# p = {"service"       : "report",
#     "report"         : "summary",
#     "reportingBasis" : "ServiceDate",
#     "reportingFrom"  : "2013-01-01",
#     "reportingTo"    : "2013-12-31",
#     "comparisonFrom" : "2012-01-01",
#     "comparisonTo"   : "2012-12-31"}

# r = das.api(p)
# r = das.to_dict(p)
# r = das.to_list(p)

r = das.response(p)
# r = das.pages(p, 1, 10)
# r = das.all(p)

print "Executed in", str(datetime.now()-timer)[:-4] + "\a\n"