import urllib2
import json


class JenkinsItem:
    def __init__(self, jobpath, data):
        self.data = data
        self.path = jobpath
        self.link = None

    def __str__(self):
        return "%s : %s" % ( self.path, self.name() )

    def name(self):
        if "name" in self.data:
            return self.data["name"]
        return None

    def jobs(self):
        rv = []
        if "jobs" in self.data:
            for jobitem in self.data["jobs"]:
                rv.append(jobitem["name"])
        return rv

    def configurations(self):
        rv = []
        if "activeConfigurations" in self.data:
            for cfgitem in self.data["activeConfigurations"]:
                rv.append(cfgitem["name"])
        return rv


class JenkinsAPI:
    def __init__(self, server):
        self.apisuffix = "/api/json"
        self.server = server

    def make_job_path(self, parent, name):
        if parent is None:
            parent = ""
        jl = "%s/job/%s" % (parent, name)
        return jl

    def list_jobs(self, parentpath=None):
        # http://MASTER/api/json?pretty=true
        # http://MASTER/job/ThingProjects/api/json?pretty=true
        # http://MASTER/job/CoolProjects/job/AlertLight/api/json?pretty=true
        if parentpath is None:
            parentpath = ""
        rv = []
        parent = self.get_item(parentpath)
        rv.extend(parent.jobs())

        return rv

    def get_item(self, address):
        page = "%s/%s/%s" % (self.server, address, self.apisuffix)
        resp = urllib2.urlopen(page)

        s = resp.read()
        jobitem = json.loads(s)

        item = JenkinsItem(address, jobitem)
        item.url = "%s/%s" % (self.server, address)

        return item

    def get_properties(self, path, proplist=[]):
        data = dict()
        # http://MASTER/job/Folder1/job/Folder2/platforms=linux-libc6.3/lastBuild/api/json?pretty=true&tree=estimatedDuration
        page = "%s/%s/%s?tree=%s" \
            % (self.server, path, self.apisuffix, ",".join(proplist))
        try:
            resp = urllib2.urlopen(page)

            s = resp.read()
            data = json.loads(s)
        except urllib2.HTTPError:
            pass

        return data

    def get_all_jobs(self, start=None):
        rv = []
        if start is None:
            start = self.get_item("")
        rv.append(start)
        for childname in start.jobs():
            childpath = "%s/job/%s" % (start.path, childname)
            child = self.get_item(childpath)
            children = self.get_all_jobs(child)
            if children:
                rv.extend(children)
        return rv

if __name__ == "__main__":
    import sys
    import pprint
    j = JenkinsAPI(sys.argv[1])

    pp = pprint.PrettyPrinter(indent=2)

    top = j.get_item("")

    for job in j.get_all_jobs(top):
        print "%s" % job
        for cfg in job.configurations():
            print " -> %s" % cfg
            res = j.get_properties("%s/%s/lastBuild" % (job.path, cfg),
                                   ["estimatedDuration", "duration",
                                    "result", "building"])
            pp.pprint(res)

