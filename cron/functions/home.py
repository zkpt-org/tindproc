import os
import pandas as pd
import numpy as np

def graph4(das, query):
    ticket = os.environ['PGT']
    
    reporting_from  = query["reportingFrom"]
    reporting_to    = query["reportingTo"]
    
    comparison_from = query["comparisonFrom"]
    comparison_to   = query["comparisonTo"]
    
    total_claims = count_claims(reporting_from, reporting_to, das)
    
    psize = total_claims / 99 if total_claims % 100 > 0 else total_claims / 100
    pages = 100
    total = 0
    results = []
    
    for p in range(1, pages+1):
        cumul = cumulative(reporting_from, reporting_to, ticket, das, p, psize)
        cailms = pd.DataFrame(cumul)[['paidAmount']]
        total += np.asscalar(cailms.sum())
        results.append({"claims" : p, "cost" : total})
    
    for row in results:
        row["cost"] = round(row["cost"]/total*100, 2)
    
    return results

def count_claims(_from, _to, das):
    params = {
        "service"  : "search", 
        "table"    : "smc",
        "page"     : "1",
        "pageSize" : "0",
        "query"    :"{'and':[{'serviceDate.gte':'" + _from + "'},{'serviceDate.lte':'" + _to + "'},{'paidAmount.gt':'0'}]}"}
    
    response = das.to_dict(params)
    return response["summary"]["totalCounts"]

def count_claimants(total, _from, _to, ticket, das):
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

def cumulative(_from, _to, ticket, das, page, psize):
    results = []
    params  = {
    "service"  : "search", 
    "table"    : "smc",
    "page"     : str(page),
    "pageSize" : str(psize),
    "order"    : "paidAmount:desc",
    "query"    : "{'and':[{'serviceDate.gte':'" + _from + "'},{'serviceDate.lte':'" + _to + "'},{'paidAmount.gt':'0'}]}",
    "fields"   : "[paidAmount]"
    }
    response = das.to_dict(params)["result_sets"]
    results += [response[row] for row in response]
    return results