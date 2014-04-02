import os, datetime, calendar
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
from lib.helpers import format_query, empty_query, claims, cohort

def graph1(das, win, q):
    reporting_from  = win["reporting_from"]
    reporting_to    = win["reporting_to"]
    
    comparison_from = win["comparison_from"]
    comparison_to   = win["comparison_to"]
    
    if empty_query(q):
        data = graph1_summary(das, win)
    else:
        # query = format_query(q, das, reporting_from, reporting_to)
        resp = claims(das, reporting_from, reporting_to)
        df = resp.dataframe()
        return df
    
    # return data

def graph2(das, win):
    reporting_from  = win["reporting_from"]
    reporting_to    = win["reporting_to"]
    
    comparison_from = win["comparison_from"]
    comparison_to   = win["comparison_to"]
    
    data = []
    
    start = datetime.date(*map(int, reporting_from.split("-")))
    end   = datetime.date(*map(int, reporting_to.split("-")))
    
    m = end-start
    
    start_month = start.month
    end_months  = (end.year-start.year) * 12 + end.month + 1
    
    months = end_months - start.month
    
    dates = [datetime.datetime(year=yr, month=mn, day=1) for (yr, mn) in (
         ((m - 1) / 12 + start.year, (m - 1) % 12 + 1) for m in range(start_month, end_months))]
    
    for d in dates:                 
        params = {
            "service"       : "report", 
            "report"        : "summary",
            "eligibilityType":"[medical]",
            "reportingBasis": "ServiceDate",
            "reportingFrom" : d.strftime("%Y-%m-%d"),
            "reportingTo"   : datetime.date(d.year, d.month, calendar.monthrange(d.year, d.month)[1]).strftime("%Y-%m-%d"),
            "comparisonFrom": (d - relativedelta(years=1)).strftime("%Y-%m-%d"),
            "comparisonTo"  : datetime.date(d.year-1, d.month, calendar.monthrange(d.year, d.month)[1]).strftime("%Y-%m-%d")}
        
        response = das.to_dict(params)
        comparison = response["comparison"][0]
        reporting  = response["reporting"][0]
        
        data.append({
            "month"  : 12 - d.month, #d.strftime("%B"),
            "date"   : d.strftime("%Y-%m-%d"),
            "total"     : round((reporting["totalPharmacyPaidAmount"]  + reporting["totalMedicalPaidAmount"])  / reporting["memberMonths"]),
            "benchmark" : round((comparison["totalPharmacyPaidAmount"] + comparison["totalMedicalPaidAmount"]) / comparison["memberMonths"])})
    
    return data

def graph3(das, win):
    reporting_from  = win["reporting_from"]
    reporting_to    = win["reporting_to"]
    
    comparison_from = win["comparison_from"]
    comparison_to   = win["comparison_to"]
    
    """Set locale."""
    try:
        import locale
        locale.setlocale(locale.LC_ALL, 'en_US.utf8')
    except Exception:
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except Exception as e:
            messages.error(request, 'An error occurred: {0}'.format(e))
    try:
        """Get data from summary table."""
        params = {
            "service"       : "report", 
            "report"        : "summary",
            "reportingBasis": "ServiceDate",
            "eligibilityType":"[medical]",
            "reportingFrom" : reporting_from,
            "reportingTo"   : reporting_to,
            "comparisonFrom": comparison_from,
            "comparisonTo"  : comparison_to}
        
        response = das.to_dict(params)
        
    except Exception, e:
        response = None
        print str(e)+"\n"
        with open("../errors.log", "a+") as f: f.write(str(e)+"\n")
    
    if response:    
        comparison = response["comparison"][0]
        reporting  = response["reporting"][0]
                
        """Calculate the number of claims for reporting Period."""
        claims = count_claims(reporting_from, reporting_to, das)        
        """Calculate the number of claimants for Reporting Period."""
        claimants = count_claimants(claims, reporting_from, reporting_to, das)
        
        """Calculate the number of claims Comparison Period."""
        claims2 = count_claims(comparison_from, comparison_to, das)
        """Calculate the number of claimants for Reporting Period."""
        claimants2 = count_claimants(claims, comparison_from, comparison_to, das)
        
        """Calculate the number of ER visits for Reporting Period."""
        er_visit = count_er_visits(reporting_from, reporting_to, das)
        """Calculate the number of ER visits for Comparison Period."""
        er_visit2 = count_er_visits(comparison_from, comparison_to, das)
        
        data = {
            "reporting":{
                "employees" : locale.format("%d", reporting["subscribers"], grouping=True),
                "members"   : locale.format("%d", reporting["members"], grouping=True),
                "totalcost" : "$" + locale.format("%d", reporting["totalMedicalPaidAmount"] + reporting["totalPharmacyPaidAmount"], grouping=True),
                "claims"    : locale.format("%d", claims, grouping=True),
                "claimants" : locale.format("%d", claimants, grouping=True),
                "avg_claims": int(round(claims / reporting["members"])),
                "er_visits" : locale.format("%d", er_visit, grouping=True),
                "avg_claim_cost": "$" + str(int(round((reporting["totalMedicalPaidAmount"] + reporting["totalPharmacyPaidAmount"]) / claims)))
            },
            "comparison":{
                "employees" : locale.format("%d", comparison["subscribers"], grouping=True),
                "members"   : locale.format("%d", comparison["members"], grouping=True),
                "totalcost" : "$" + locale.format("%d", comparison["totalMedicalPaidAmount"] + comparison["totalPharmacyPaidAmount"], grouping=True),
                "claims"    : locale.format("%d", claims2, grouping=True),
                "claimants" : locale.format("%d", claimants2, grouping=True),
                "avg_claims": int(round(claims2 / comparison["members"])),
                "er_visits" : locale.format("%d", er_visit2, grouping=True),
                "avg_claim_cost": "$" + str(int(round((comparison["totalMedicalPaidAmount"] + comparison["totalPharmacyPaidAmount"]) / claims)))
            }
        }
        
        return data

def graph4(das, win, q):
    reporting_from  = win["reporting_from"]
    reporting_to    = win["reporting_to"]
    
    comparison_from = win["comparison_from"]
    comparison_to   = win["comparison_to"]
    
    query = format_query(q, das, reporting_from, reporting_to)
    cond  = q['condition']
    
    total_claims = count_claims(reporting_from, reporting_to, query, cond, das)
    
    psize = total_claims / 99 if total_claims % 100 > 0 else total_claims / 100
    pages = 100
    total = 0
    results = []
    
    for p in range(1, pages+1):
        cumul = cumulative(reporting_from, reporting_to, query, cond, das, p, psize)
            
        if cumul:
            cailms = pd.DataFrame(cumul)[['paidAmount']]
            total += np.asscalar(cailms.sum())
            results.append({"claims" : p, "cost" : total})
        # else:
        #     return "No Data"
        
    for row in results:
        row["cost"] = round(row["cost"]/total*100, 2)
    
    return results

def count_claims(_from, _to, query, cond, das):
    params = {
        "service"  : "search", 
        "table"    : "smc",
        "page"     : "1",
        "pageSize" : "0",
        "query"    : "{'and':[{'serviceDate.gte':'" + _from + "'},{'serviceDate.lte':'" + _to + "'},{'paidAmount.gt':'0'},"+query}
    params = cohort(das, cond, params)
    response = das.to_dict(params)
    return response["summary"]["totalCounts"]

def count_claimants(total, _from, _to, das):
    params = {
    "service"     : "search",
    "table"       : "ms",
    "page"        : "1",
    "pageSize"    : "0",
    "query"       : "{'and':[{'serviceDate.gte':'" + _from + "'},{'serviceDate.lte':'" + _to + "'},{'paidAmount.gt':'0'}]}",
    "fields"      : "[memberId]",
    "report"      : "viewMemberSearch",
    "recordTypes" : "smc"}
    
    response = das.to_dict(params)["summary"]["totalCounts"]
    return response

def cumulative(_from, _to, query, cond, das, page, psize):
    results = []
    
    params  = {
    "service"  : "search", 
    "table"    : "smc",
    "page"     : str(page),
    "pageSize" : str(psize),
    "order"    : "paidAmount:desc",
    "query"    : "{'and':[{'serviceDate.gte':'" + _from + "'},{'serviceDate.lte':'" + _to + "'},{'paidAmount.gt':'0'},"+query,
    "fields"   : "[paidAmount]",
    }
    params = cohort(das, cond, params)
    
    response = das.to_dict(params)["result_sets"]
    results += [response[row] for row in response]
    return results

def count_er_visits(_from, _to, das):
    params = {
        "service"  : "search", 
        "table"    : "smc",
        "page"     : "1",
        "pageSize" : "0",
        "query"    : "{'and':[{'serviceDate.gte':'" + _from + "'},{'serviceDate.lte':'" + _to + "'},{'erVisit.gt':0}]}"}
    
    return das.to_dict(params)["summary"]["totalCounts"]

def graph1_summary(das, win):
    reporting_from  = win["reporting_from"]
    reporting_to    = win["reporting_to"]
    
    comparison_from = win["comparison_from"]
    comparison_to   = win["comparison_to"]
    
    params = {
        "service"       : "report", 
        "report"        : "summary",
        "reportingBasis": "ServiceDate",
        "eligibilityType":"[medical]",
        "reportingFrom" : reporting_from,
        "reportingTo"   : reporting_to,
        "comparisonFrom": comparison_from,
        "comparisonTo"  : comparison_to}
    
    response = das.to_dict(params)
    comparison = response["comparison"][0]
    reporting  = response["reporting"][0]
    
    data = [
        {
            "Period"         : "Reporting",
            "Inpatient"      : round(reporting["Inpatient"] / reporting["memberMonths"]) if reporting["memberMonths"]!=0 else 0,
            "Outpatient"     : round(reporting["Outpatient"] / reporting["memberMonths"]) if reporting["memberMonths"]!=0 else 0,
            "Office Visit"   : round(reporting["Office"] / reporting["memberMonths"]) if reporting["memberMonths"]!=0 else 0,
            "Pharmacy Claims": round(reporting["totalPharmacyPaidAmount"] / reporting["memberMonths"]) if reporting["memberMonths"]!=0 else 0,
        },
        {
            "Period"         : "Comparison",
            "Inpatient"      : round(comparison["Inpatient"] / comparison["memberMonths"]) if comparison["memberMonths"]!=0 else 0,
            "Outpatient"     : round(comparison["Outpatient"] / comparison["memberMonths"]) if comparison["memberMonths"]!=0 else 0,
            "Office Visit"   : round(comparison["Office"] / comparison["memberMonths"]) if comparison["memberMonths"]!=0 else 0,
            "Pharmacy Claims": round(comparison["totalPharmacyPaidAmount"] / comparison["memberMonths"]) if comparison["memberMonths"]!=0 else 0,
        },
    ]
    return data
