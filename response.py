class DasResponse(object):
    def __init__(self, das, p):
        import json
        self.raw  = das.api(p)
        self.data = json.loads(self.raw)
        self.parse(self.data)
        self.page  = int(p["page"]) if "page" in p else None
        self.size  = int(p["pageSize"]) if "pageSize" in p else None
        self.pages = self.total / self.size + 1 if self.total % self.size != 0 else self.total / self.size
        self.query = das.call
        
    def parse(self, data):
        if 'result_sets' in data:
            self.results = [Entry(**data['result_sets'][i]) for i in data['result_sets']]
            self.data['result_sets'] = [data['result_sets'][i] for i in data['result_sets']]
        
        if 'summary' in data:
            self.querytime  = self.queryTime     = data['summary']['queryTime']
            self.rendertime = self.renderingTime = data['summary']['renderingTime']
            self.total      = self.totalCounts   = data['summary']['totalCounts']
            self.summary    = data['summary']
    
    def dataframe(self):
        import pandas as pd
        return pd.DataFrame(self.data['result_sets'])
    
    def get_pages(self, x, y):
        
    def all_pages(self):
        
    
    def __str__(self):
        attrs = vars(self)
        data = str(self.data)[:50]+'...}' if len(str(self.data)) > 50 else str(self.data)
        raw  = self.raw[:50]+'...}' if len(self.raw) > 50 else self.raw
        # res  = '\n'.join([s.__str__() for s in self.results])
        res  = str(len(self.results)) + " entries... [call DasResponse.results or DasResponse.dump() to inspect full set.]"
        smr  = ','.join(" %s: %s" % i for i in sorted(self.summary.items()))
        
        return '\n<DasResponse object>\n' + \
        "  query:   "  + self.query + "\n"  + \
        "  page:    "  + str(self.page) + " of " +  str(self.pages) + "\n"  + \
        "  data:    "  + data + "\n"  + \
        "  raw:     "  + raw  + "\n"  + \
        "  results: "  + res  + "\n"  + \
        "  summary:"   + smr  + "\n"
    
    def __repr__(self):
        return self.__str__()
    
    def dump(self):
        if self.results:
            print ('\n<DasResponse object>' + '\n\n<DasResponse.summary dict>\n' +
            '\n'.join("  %s: %s" % i for i in sorted(self.summary.items())) + 
            '\n\n<DasResponse.results list>' +
            '\n'.join(s.__str__() for s in self.results))

class Entry(object):
    def __init__(self, **entries): 
        self.__dict__.update(entries)
    
    def dump(self):
        print self.__str__()
    
    def __str__(self):
        attrs = vars(self)
        return '\n<Entry object>\n' + '\n'.join("  %s: %s" % item for item in sorted(attrs.items()))
    
    def __unicode__(self):
        attrs = vars(self)
        return u'\n<Entry object>\n' + u'\n'.join("  %s: %s" % item for item in sorted(attrs.items()))
        
    def __repr__(self):
        return self.__str__()
