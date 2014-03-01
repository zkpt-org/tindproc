class DasResponse(object):
    def __init__(self, das, p):
        import json
        self.DEFAULT_PAGE_SIZE = 20
        self.type = p['service'] if 'service' in p else 'search'
        self.raw  = das.api(p)
        self.data = json.loads(self.raw)
        self.query = das.call
        
        if self.type == "search":
            self.parse(self.data)
            self.page  = int(p["page"]) if "page" in p else 1
            self.size  = int(p["pageSize"]) if "pageSize" in p else self.DEFAULT_PAGE_SIZE
            self.pages = self.numpages(self.size)
        else:
            self.page  = None
            self.size  = None
            self.pages = None
            self.results    = None
            self.summary    = None
            self.querytime  = self.queryTime     = None
            self.rendertime = self.renderingTime = None
            self.total      = self.totalCounts   = None
    
    def nullset(self):
        self.page  = 0
        self.size  = 0
        self.pages = 0
        self.results    = []
        self.summary    = ""
        self.querytime  = self.queryTime     = 0
        self.rendertime = self.renderingTime = 0
        self.total      = self.totalCounts   = 0
    
    def numpages(self, *args):
        if self.type != "search":
            self.DasResponseTypeError(self.__class__.__name__ + ".numpages")
        else:
            if len(args) > 0 and args[0] != None:
                size = int(args[0]) if int(args[0]) != 0 else self.DEFAULT_PAGE_SIZE
            else:
                size = self.DEFAULT_PAGE_SIZE
            pages = (self.total / size + 1 if self.total % size != 0 else self.total / size)
            return pages
        
    def parse(self, data):
        if 'result_sets' in data:
            self.results = [Entry(**data['result_sets'][i]) for i in data['result_sets']]
            self.data['result_sets'] = [data['result_sets'][i] for i in data['result_sets']]
        else:
            self.results = []
            self.data['result_sets'] = []
        
        if 'summary' in data:
            self.querytime  = self.queryTime     = data['summary']['queryTime']
            self.rendertime = self.renderingTime = data['summary']['renderingTime']
            self.total      = self.totalCounts   = data['summary']['totalCounts']
            self.summary    = data['summary']
        else:
            self.querytime  = self.queryTime     = 0
            self.rendertime = self.renderingTime = 0
            self.total      = self.totalCounts   = 0
            self.summary    = None
    
    def list(self, prop):
        return [getattr(n, prop) for n in self.results if n.hasprop(prop)]
    
    def dropnull(self, prop):
        return [n for n in self.results if n.hasprop(prop)]
    
    def dataframe(self):
        if self.type == "search":
            import pandas as pd
            return pd.DataFrame(self.data['result_sets'])
        else:
            self.DasResponseTypeError(self.__class__.__name__ + ".dataframe")
    
    def DasResponseTypeError(self, name):
        raise Exception( "<function "+name+">" + " cannot be called on <DasResponse object> of type: '"+self.type+"'")
    
    def __str__(self):
        # attrs = vars(self)
        data  = str(self.data)[:50]+'...}' if len(str(self.data)) > 50 else str(self.data)
        raw   = self.raw[:50]+'...}' if len(self.raw) > 50 else self.raw
        query = self.query[:79]+'...' if len(self.query) > 50 else self.query
        
        if self.type == "search":
            # res  = '\n'.join([s.__str__() for s in self.results])
            res  = str(len(self.results)) + " entries... [call DasResponse.results or DasResponse.dump() to inspect full set.]"
            smr  = ','.join(" %s: %s" % i for i in sorted(self.summary.items())) if self.summary else None
        
            return '\n<DasResponse object>\n' + \
            "  query:   "  + query + "\n"  + \
            "  page:    "  + str(self.page) + " of " +  str(self.pages) + "\n"  + \
            "  data:    "  + data + "\n"  + \
            "  raw:     "  + raw  + "\n"  + \
            "  results: "  + res  + "\n"  + \
            "  summary: "  + str(smr) + "\n"
        else:
            return '\n<DasResponse object>\n' + \
            "  query:   "  + query + "\n"  + \
            "  data:    "  + data  + "\n"  + \
            "  raw:     "  + raw   + "\n"
            
    def __repr__(self):
        return self.__str__()
    
    def dump(self):
        if self.type == "search":
            print ('\n<DasResponse object>' + '\n\n<DasResponse.summary dict>\n' +
            '\n'.join("  %s: %s" % i for i in sorted(self.summary.items())) + 
            '\n\n<DasResponse.results list>' +
            '\n'.join(s.__str__() for s in self.results))
        else:
            from pprint import pprint
            pprint(self.data)

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
    
    def hasprop(self, prop):
        if hasattr(self, prop):
            return True
        return False
