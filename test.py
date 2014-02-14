import IPython.core.ipapi
# from pprint import pprint
ipython = IPython.core.ipapi.get()
ipython.magic('%load_ext autoreload')
ipython.magic('%autoreload 2')

from das import Das
# das = Das()
# das.auth()

p = {"service" : "search", "table" : "ms", "page" : "1", "pageSize" : "10"}

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
