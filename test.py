import IPython.core.ipapi, os #, time
from datetime import datetime

ipython = IPython.core.ipapi.get()
ipython.magic('%load_ext autoreload')
ipython.magic('%autoreload 2')

from das import Das
if 'PGT' not in os.environ:
    das = Das()
    das.auth()
    os.environ['PGT'] = das.PGT
else:
    das = Das()
    das.PGT = os.environ['PGT']

p = {"service" : "search", "table" : "ms"}
# p = {"service" : "search", "table" : "ms", "page" : "1", "pageSize" : "10"}
# p = {"service"       : "report",
#     "report"         : "summary",
#     "reportingBasis" : "ServiceDate",
#     "reportingFrom"  : "2013-01-01",
#     "reportingTo"    : "2013-12-31",
#     "comparisonFrom" : "2012-01-01",
#     "comparisonTo"   : "2012-12-31"}

timer = datetime.now()
# r = das.api(p)
# r = das.to_dict(p)
# r = das.to_list(p)

# r = das.response(p)
# r = das.pages(p, 1, 10)
r = das.all(p)

print "Executed in", str(datetime.now()-timer)[:-4] + "\a\n"