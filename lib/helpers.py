import datetime, calendar, copy, json
from dateutil.relativedelta import relativedelta
from collections import OrderedDict

def lastdate(das):
    try:
        params = {
            "service"  : "search", 
            "table"    : "smc",
            "page"     : "1",
            "pageSize" : "1",
            "order"    : "paidDate:desc"}
        
        return das.to_dict(params)["result_sets"]["0"]["serviceDate"]
    
    except Exception,e:
        print str(e)+"\n"
        with open("../errors.log", "a+") as f: f.write(str(e)+"\n")

def timewindow(das):
    """Get the last date recorded in the dataset."""
    ld = lastdate(das)
    d  = datetime.datetime.strptime(ld, "%Y-%m-%d")
    """Set to last day of the month."""
    last = datetime.date(d.year, d.month, calendar.monthrange(d.year, d.month)[1])
    
    """Set reporting and comparison time windows."""
    reporting_to    = last.strftime("%Y-%m-%d")
    reporting_from  = (last-relativedelta(years=1)+relativedelta(days=1)).strftime("%Y-%m-%d") 
    comparison_from = (last-relativedelta(years=2)+relativedelta(days=1)).strftime("%Y-%m-%d")
    comparison_to   = (last-relativedelta(years=1)).strftime("%Y-%m-%d")
    
    return {"reporting_from" : reporting_from, "reporting_to" : reporting_to, 
            "comparison_from" : comparison_from, "comparison_to" : comparison_to}

def chronic(das, win):
    from collections import OrderedDict
    p = {
    "service":"report",
    "report":"chronicConditions",
    "reportingBasis":"ServiceDate",
    "reportingFrom":win["reporting_from"],
    "reportingTo":win["reporting_to"],
    "comparisonFrom":win["comparison_from"], 
    "comparisonTo":win["comparison_to"],
    "order" : "Admits:desc",
    }
    r = das.response(p)
    conditions = OrderedDict()
    
    for i in sorted(r.data["reporting"]["Default"], key=lambda x: r.data["reporting"]["Default"][x]["withCondition"] 
        if x != "memberCount" and x != "memberMonths" else r.data["reporting"]["Default"][x], reverse=True): 
        if i != "memberCount" and i != "memberMonths":
            # print r.data["reporting"]["Default"][i]["description"], r.data["reporting"]["Default"][i]["withCondition"]
            conditions.update({r.data["reporting"]["Default"][i]["name"] : r.data["reporting"]["Default"][i]["description"]})
    return conditions

def employers(das, win):
    p = {
    "service"     : "search",
    "table"       : "ms",
    "page"        : "1",
    "pageSize"    : "100",
    "query"       : "{'and':[{'serviceDate.gte':'"+win["reporting_from"]+"'},{'serviceDate.lte':'"+win["reporting_to"]+"'}]}",
    "fields"      : "[groupIdName,groupId]"
    }
    emp = das.all(p)
    
    return list(set([(i.groupIdName, i.groupId) for i in emp.results if 'groupIdName' in vars(i)]))

def format_query(q):
    query = ""
    
    for key, val in q.items():
        if val != "ALL":
            if key == "client":
                if val == "ABC corporation":
                    client_id = '01'
                if val == "XYZ private ltd":
                    client_id = '02'
                query += "{'groupId.eq':'"+client_id+"'},"
            elif key == "office":
                pass
            elif key == "level":
                pass
            elif key == "gender":
                query += "{'memberGender.eq':'"+val[0]+"'},"
            elif key == "age":
                if val != "70+":
                    val.split('-')[0]
                    query += "{'memberAge.gte':'"+val.split('-')[0]+"'},{'memberAge.lte':'"+val.split('-')[1]+"'},"
                else:
                    query += "{'memberAge.gte':'"+val[:2]+"'},"
            elif key == "condition":
                query += "{'qmMeasure.eq':'"+val+"'},"
    # if q["condition"] != "ALL":
    #         # p = {
    #         # "service":"search",
    #         # "table":"ms",
    #         # "query":"{'and':[{'serviceDate.gte':'" + _from + "'},{'serviceDate.lte':'" + _to + "'},{'qmMeasure.eq':'"+val+"'}]}",
    #         # "fields"   : "[memberId]"}
    #         # 
    #         # members = das.all(p).list('memberId')
    #         # # if len(members) > 50:
    #         # #     for chunk in chunks(members, 50):
    #         # #         query2 =   query + "{'memberId.eq':[" + ",".join(["'"+m+"'" for m in chunk])+"]},"
    #         # #         queries.append(query2)
    #         # query += "{'memberId.eq':[" + ",".join(["'"+m+"'" for m in members])+"]},"
    #         
    #         p = {
    #         "service":"create",
    #         "table":"ms",
    #         "query":"{'and':[{'qmMeasure.eq':'"+q["condition"]+"'}]}"}
    #         # "query":"{'and':[{'serviceDate.gte':'" + _from + "'},{'serviceDate.lte':'" + _to + "'},{'qmMeasure.eq':'"+val+"'}]}"}
    #         cohort = das.to_dict(p)["cohortId"]
    #         query += "]}&cohortId=" + cohort
    # else:
    # query += "]}"
    return query

def get_cohort(sql, das, q):
    traits = copy.deepcopy(q)
    if "start_date" in traits: del traits["start_date"]
    if "end_date" in traits:   del traits["end_date"]
    
    if all(v == 'ALL' for v in traits.values()):
        return None
    
    for key, val in traits.items():
        if val == 'ALL':
            del traits[key]
            
    o = OrderedDict(sorted([(key, val) for key, val in traits.items()]))
    t = json.dumps(o)
    
    if not sql.select(table='data_cohort', where="traits='%s'" % t):        
        print "creating new cohort."
        query = format_query(q)
        cohort = das.cohort(query)
        p = {
            "service":"create",
            "table":"ms",
            "query":"{'and':[%s]}" % query
        }
        cohort = das.to_dict(p)["cohortId"]
        sql.insert(table='data_cohort', rows=[{'cohort_id':cohort,'traits':t}])
    else:
        print "cohort exists", cohort
        cohort = sql.select(table='data_cohort', where="traits='%s'" % t)[0][1]
    return cohort

def cohort(das, cond):
    if cond != "ALL":            
        p = {
        "service":"create",
        "table":"ms",
        "query":"{'and':[{'qmMeasure.eq':'"+cond+"'}]}"}
        cohort = das.to_dict(p)["cohortId"] 
    else:
        cohort = None
    return cohort

def add_cohort(cohort, params):
    if cohort is not None: 
        params.update({"cohortId":cohort})
    return params

def empty_query(query):
    if(query['client']!='ALL' or query['office']!='ALL' or query['level']!='ALL' or 
       query['gender']!='ALL' or query['age']!='ALL' or query['condition']!='ALL'):
       return False
    return True

def claims(das, _from, _to, query, cohort):
    """get all claims for the time period specified."""
    params = {
        "service"  : "search", 
        "table"    : "smc",
        "pageSize" : "100",
        "query"    : "{'and':[{'serviceDate.gte':'" + _from + "'},{'serviceDate.lte':'" + _to + "'},"+query}
        # "query"    : "{'and':[{'serviceDate.gte':'" + _from + "'},{'serviceDate.lte':'" + _to + "'},{'paidAmount.gt':'0'},"+query} 
    
    params = add_cohort(cohort, params)
    return das.all(params)

def months(_from, _to):
    start = datetime.date(*map(int, _from.split("-")))
    end   = datetime.date(*map(int, _to.split("-")))
    
    m = end-start
    
    start_month = start.month
    end_months  = (end.year-start.year) * 12 + end.month + 1
    
    months = end_months - start.month
    
    # dates = [datetime.datetime(year=yr, month=mn, day=1) for (yr, mn) in (
    #      ((m - 1) / 12 + start.year, (m - 1) % 12 + 1) for m in range(start_month, end_months))]
    
    return months

def chunks(l, n):
    """ Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

    