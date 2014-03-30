import urllib2
import json

class JenkinsItem:
    def __init__(self, jobpath, data):
        self.data = data
        self.path = jobpath

    def __str__(self):
        return "%s : %s" % ( self.path, self.name() )

    def name(self):
        if "name" in self.data:
            return self.data["name"]
        return None

    def jobs(self):
        rv = []
        if "jobs" in self.data:
            for job in self.data["jobs"]:
                rv.append( job["name"] )
        return rv

    def configurations(self):
        rv = []
        if "activeConfigurations" in self.data:
            for cfg in self.data["activeConfigurations"]:
                rv.append( cfg["name"] )
        return rv

class JenkinsAPI:

    def __init__(self, server):
        self.apisuffix = "/api/json"
        self.server = server

    def make_job_path(self, parent, name):
        if parent is None:
            parent = ""
        jl = "%s/job/%s" % ( parent, name )
        return jl

    def list_jobs(self, parentpath=None):
        # http://triffid.ncipher.com:8080/api/json?pretty=true
        # http://triffid.ncipher.com:8080/job/nShieldProjects/api/json?pretty=true
        # http://triffid.ncipher.com:8080/job/nShieldProjects/job/AlertLight/api/json?pretty=true
        if parentpath is None:
            parentpath = ""
        rv = []
        parent = self.get_item(parentpath)

        for job in parent.jobs():
            rv.append(job)
        #    path = self.make_job_path( parent, job )
        #    child = self.get_item(path)
        #    rv.append(child)
    
        return rv

    def get_item(self, address):
        page = "%s/%s/%s" %( self.server, address, self.apisuffix )
        resp = urllib2.urlopen( page )

        s =  resp.read()
        job = json.loads(s)

        item = JenkinsItem(address, job)

        return item

    def get_properties(self, path, proplist=[]):
        data = dict()
        # http://elsted.ncipher.com:8080/job/nShieldProjects/job/MainlineHostSoftware/platforms=linux-libc6.3/lastBuild/api/json?pretty=true&tree=estimatedDuration
        page = "%s/%s/%s?tree=%s" \
            % ( self.server, path, self.apisuffix, ",".join(proplist) )
        try:
            resp = urllib2.urlopen( page )

            s = resp.read()
            data = json.loads(s)
        except (urllib2.HTTPError):
            pass

        return data


    def get_all_jobs(self, start=None):
        rv = []
        if start is None:
            start = self.get_item("")
        rv.append(start)
        for childname in start.jobs():
            childpath = "%s/job/%s" %( start.path, childname )
            child = self.get_item(childpath)
            children = self.get_all_jobs( child )
            if children:
                rv.extend(children)
        return rv

if __name__ == "__main__":
    j = JenkinsAPI("http://triffid.ncipher.com:8080")

    import pprint
    pp = pprint.PrettyPrinter(indent=2)

    top = j.get_item("")

    for job in j.get_all_jobs(top):
        print "%s" % job
        for cfg in job.configurations():
            print " -> %s" % cfg
            res = j.get_properties( "%s/%s/lastBuild" % (job.path, cfg),
                    ["estimatedDuration", "duration", "result", "building"] )
            pp.pprint( res )

