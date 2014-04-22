class DasCohort:
    def __init__(self, das, id=None):
        self.id  = id
        self.das = das
        
    def create(self, query):
        """Create a new cohort."""
        p = {"service":"create", "table":"ms", "query":"{'and':[%s]}" % query}
        self.id = self.das.to_dict(p)["cohortId"]
        
        p = {"service":"search", "table":"ms", "pageSize":"100", "fields":"[memberId]", "query":"{'and':[%s]}" % query}
        members = self.das.all(p).list('memberId')
        self.update(add=members)
        
        return self
        
    def update(self, add=None, remove=None):
        """Update an existing cohort with list of members to be added or removed."""
        if add:
            if len(add) > 50:
                for chunk in self.chunks(add, 50):
                    memberIds = "[" + ",".join(['"' + a + '"' for a in chunk]) + "]"
                    p = {"service" : "update", "memberIds" : memberIds, "cohortId" : self.id}
                    r = self.das.api(p)
            else:
                memberIds = "[" + ",".join(['"' + a + '"' for a in add]) + "]"
                p = {"service" : "update", "memberIds" : memberIds, "cohortId" : self.id}
                r = self.das.api(p)
        
        if remove:
            if len(remove) > 50:
                for chunk in self.chunks(remove, 50):
                    memberIds_removed = "[" + ",".join(["'" + rm + "'" for rm in chunk]) + "]" 
                    p = {"service" : "update", "memberIds_removed" : memberIds_removed, "cohortId" : self.id}
                    r = self.das.api(p)
            else:
                memberIds_removed = "[" + ",".join(['"' + a + '"' for a in add]) + "]"
                p = {"service" : "update", "memberIds_removed" : memberIds_removed, "cohortId" : self.id}
                r = self.das.api(p)
        
    def delete(self, id=None):
        """Delete the cohort with the specified member id."""
        p = {
            "service"  : "delete",
            "cohortId" : self.id if id is None else id
            }
        self.das.api(p)
        print "Cohort", self.id, "deleted."
        return self.id
        
    def chunks(self, l, n):
        """ Yield successive n-sized chunks from l."""
        for i in xrange(0, len(l), n):
            yield l[i:i+n]