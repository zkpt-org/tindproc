import datetime, calendar
from dateutil.relativedelta import relativedelta

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
    conditions = []
    
    for i in sorted(r.data["reporting"]["Default"], key=lambda x: r.data["reporting"]["Default"][x]["withCondition"] 
        if x != "memberCount" and x != "memberMonths" else r.data["reporting"]["Default"][x], reverse=True): 
        if i != "memberCount" and i != "memberMonths":
            # print r.data["reporting"]["Default"][i]["description"], r.data["reporting"]["Default"][i]["withCondition"]
            conditions.append(r.data["reporting"]["Default"][i]["description"])
    return conditions
# def top20diagnosis(das, win):
    

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

def format_query(q, das, _from, _to):
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
                p = {
                "service":"search",
                "table":"ms",
                "query":"{'and':[{'serviceDate.gte':'" + _from + "'},{'serviceDate.lte':'" + _to + "'},{'primaryDiagnosis.eq':'"+val+"'}]}}",
                "fields"   : "[memberId]"}

                members = das.all(p).list('memberId')
                # query  += "{'or':["+",".join(["{'memberId.eq':'"+m+"'}" for m in members])+"]},"
                query  += "{'or':[{'memberId.eq':'[" + ",".join([m for m in members])+"]'}]},"
                # query += "{'or':[{'memberId.eq':'0x8c11b6d71a5951f3af507d23d49ddf24'}]},"
                # query  = "{'and':[{'or':["+query+"]}]},"
                # query += "{'primaryDiagnosis.eq':'"+val+"'},"
    return query