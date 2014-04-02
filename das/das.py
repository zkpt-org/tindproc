import urllib, pycurl, cStringIO, os, config, copy
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from response import DasResponse
#from django.http import QueryDict

class Das:
    def __init__(self):
        import config
        self.USER     = config.user
        self.PASS     = config.pwrd
        self.HOST     = 'tind-lite.zakipoint.com'
        self.TICKETS  = 'https://login.deerwalk.com/cas/v1/tickets'
        self.SERVICE  = 'https://tind-lite.zakipoint.com'
        self.PROXY    = 'https://proxy.zakipoint.com/'
        self.VALIDATE = 'https://login.deerwalk.com/cas/serviceValidate'
        self.API_URL  = 'https://das.deerwalk.com'
        self.PT_URL   = 'https://login.deerwalk.com/cas/proxy'
        
        self.CLIENT_ID   = '2000'
        self.CLIENT_NAME = 'tind'
        
        # self.HOST     = 'sdemo.makalu.deerwalk.com'
        # self.TICKETS  = 'https://login.deerwalk.com/cas/v1/tickets'
        # self.SERVICE  = 'https://sdemo.makalu.deerwalk.com'
        # self.CLIENT_NAME = 'sdemo'
        
    def auth(self):
        response = self.get_ticket_granting_ticket(self.USER, self.PASS)
        
        html = BeautifulSoup(response)
        tgt  = html.body.form["action"]
        
        st  = self.get_service_ticket(tgt)
        vld = self.validate_service(st)
        xml = BeautifulStoneSoup(vld)
        iou = xml.find('cas:proxygrantingticket').string if xml.find('cas:proxygrantingticket') else None
        self.PGT = self.get_proxy_granting_ticket(iou)
        return self.PGT
    
    def curl(self, url, p, peer=False, post=False):
        response = cStringIO.StringIO()
        c = pycurl.Curl()
        if post:
            c.setopt(c.URL, str(url))
            c.setopt(c.POSTFIELDS, urllib.urlencode(p))
            # c.setopt(c.HTTPPOST, urllib.urlencode(p))
        else:
            c.setopt(c.URL, url + '?' + urllib.urlencode(p))
        if not peer: c.setopt(c.SSL_VERIFYPEER , 0)
        c.setopt(c.SSLVERSION, 3)
        c.setopt(c.WRITEFUNCTION, response.write)
        try:
            c.perform()
        except pycurl.error, error:
            errno, errstr = error
            print 'A curl error occurred: ', errstr
        c.close()
        return response.getvalue()
    
    def get_ticket_granting_ticket(self, user, password):
        p = {'username':user, 'password':password, 'hostUrl':self.HOST}
        return self.curl(self.TICKETS, p, post=True)
    
    def get_service_ticket(self, tgt):
        p = {"service":self.SERVICE}
        return self.curl(tgt, p, post=True)
    
    def validate_service(self, st):
        p = {"service":self.SERVICE, "ticket":st, "pgtUrl":self.PROXY}
        return self.curl(self.VALIDATE, p)
    
    def get_proxy_granting_ticket(self, iou):
        p = {"iou":iou}
        return self.curl('https://proxy.zakipoint.com/ticket/get/', p)
    
    def get_proxy_ticket(self):
        p = {'targetService':self.API_URL, 'pgt':self.PGT}
        rsp = self.curl(self.PT_URL, p)
        xml = BeautifulStoneSoup(rsp)
        pt = xml.find('cas:proxyticket').string if xml.find('cas:proxyticket') else xml
        return str(pt)
    
    def api(self, p):
        """Make API call, return the result string."""
        q = copy.deepcopy(p)
        
        for k, v in q.iteritems(): 
            if isinstance(v, list): q[k] = str(v[0])
        
        service = q['service'] if 'service' in q else "search"
        
        if 'service' in q: del q['service']
        
        if service == "search":
            url = self.API_URL + "/memberSearch/"
        elif service == "report":
            url = self.API_URL + "/esReport/"
        elif service == "create":
            url = self.API_URL + "/cohort/create/"
        elif service == "update":
            url = self.API_URL + "/cohort/update/"
        elif service == "delete":
            url = self.API_URL + "/cohort/delete/"
        elif service == "config":
            url = self.API_URL + "/config/"
        else:
            url = self.API_URL + "/memberSearch/"
        
        q['ticket']     = self.get_proxy_ticket()
        q['clientName'] = self.CLIENT_NAME
        q['clientId']   = self.CLIENT_ID
        
        self.call = url + "?" + urllib.urlencode(q)
        print urllib.unquote(self.call) + "\n"
        
        # response = self.curl(url, q, peer=True, post=True)
        response = self.curl(url, q, peer=True)
        # print response
        return response
    
    def to_dict(self, p):
        """Make API call and return result string as a dictionary."""
        import json
        data = self.api(p)
        return json.loads(data)
        
    
    def to_list(self, p):
        """Make API call and return result_sets as a list of dictionaries."""
        response = self.to_dict(p)
        data = [response['result_sets'][n] for n in response['result_sets']]
        return data
    
    def response(self, p):
        """Make API call and return a DasResponse object."""
        response = DasResponse(self, p)
        return response
    
    def all(self, p):
        """Get all records from the database."""
        q = copy.deepcopy(p)
        q['page'], q['pageSize'] = '1', '0'
        """Create an DasResponse instance with page size 0. to claculate number of pages."""
        r = DasResponse(self, q)
        """Use 'pageSize' if the page size was provided, else use default page size."""
        pages = r.numpages(p['pageSize'] if 'pageSize' in p else None)
        return self.pages(p, 1, pages)
    
    def pages(self, p, x, y):
        """Get records contained in the indicated pages."""
        if p['service'] == 'search':
            responses = []
            if y < x: y = x
            for page in range(x, y+1):
                p["page"] = str(page)
                responses.append(DasResponse(self, p))
            return self.concat(responses)
        else:
            DasResponse(self, p).DasResponseTypeError(self.__class__.__name__ + ".pages")
    
    def concat(self, responses):
        """Flatten responses from a multipage query into one response."""
        concat0 = []
        concat1 = []
        concat2 = []
        qtime = 0.0
        rtime = 0.0
        
        for r in responses:
            concat0 += r.results
            concat1 += r.data['result_sets']
            concat2.append(r.raw)
            qtime += r.querytime
            rtime += r.rendertime
        
        # if responses:    
        r.results = concat0
        r.raw = "[" + ",".join(concat2) + "]"
        
        if 'result_sets' in r.data:
            r.data['result_sets'] = concat1
        if 'summary' in r.data:
            r.querytime  = r.queryTime     = r.data['summary']['queryTime']     = qtime
            r.rendertime = r.renderingTime = r.data['summary']['renderingTime'] = rtime
        return r
        # else:
        #     return DasResponse(self, {}).nullset()
    
    def api_call(self, p):
        for k, v in p.iteritems(): 
            if isinstance(v, list): p[k] = str(v[0])
        
        if p['service'] == "search":
            url = self.API_URL + "/memberSearch/"
        elif p['service'] == "report":
            url = self.API_URL + "/esReport/"
        elif p['service'] == "create":
            url = self.API_URL + "/cohort/create/"
        elif p['service'] == "update":
            url = self.API_URL + "/cohort/update/"
        elif p['service'] == "delete":
            url = self.API_URL + "/cohort/delete/"
        elif p['service'] == "config":
            url = self.API_URL + "/config/"
        else:
            url = self.API_URL + "/memberSearch/"
        
        del p['service']
        
        p['ticket']     = self.get_proxy_ticket()
        p['clientName'] = self.CLIENT_NAME
        p['clientId']   = self.CLIENT_ID
        
        self.call = url + "?" + urllib.urlencode(p)
        return url + "?" + urllib.urlencode(p)
    
