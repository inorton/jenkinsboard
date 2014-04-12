"""
jenkins visualisation board - inb@ncipher.com 2014
"""
#!/usr/bin/env python

import web
import json

import jenkins

server = "http://triffid.ncipher.com:8080"

from web import form

globals = { }

app = web.auto_application()
render = web.template.render("templates/", base="master", globals = globals)

class index(app.page):
    path = '/'

    def GET(self):
        return render.index(None)

class selected(app.page):
    path = "/selected/(.+)"
    def GET(self,boardname):
        jl = jenkins.JenkinsAPI( server )
        jobs = jl.get_all_jobs()
        web.header("Content-Type", "application/json")
        rv = []
        for job in jobs:
            if not job:
                continue
            if not job.name():
                continue
            params = jl.get_properties( job.path, ["actions[parameterDefinitions[*]]"] )

            if "actions" in params:
                for pd in params["actions"]:
                    if "parameterDefinitions" in pd:
                        plist = pd["parameterDefinitions"]
                        for param in plist:
                            if "name" in param:
                                if param["name"] == "jenkinsboard":
                                    if param["description"] == boardname:
                                        rv.append( { 
                                            "name" : job.name(),
                                            "configs" : job.configurations(),
                                            "path" : job.path,
                                            "link" : server + "/" + job.path,
                                        })


        return json.dumps(rv)


class jobs(app.page):
    path = "/jobs/"
    def GET(self):
        jl = jenkins.JenkinsAPI( server )
        jobs = jl.get_all_jobs()
        web.header("Content-Type", "application/json")
        rv = []
        for job in jobs:
            rv.append( { 
                "name" : job.name(),
                "path" : job.path,
                "configs" : job.configurations(),
                "link" : server + "/" + job.path,
                })

        return json.dumps(rv)

class job(app.page):
    path = "/job/(.+)"

    def GET(self, jobpath):
        jl = jenkins.JenkinsAPI( server )
        job = jl.get_item( jobpath );
        web.header("Content-Type", "application/json")
        return json.dumps(job.data)

class status(app.page):
    path = "/status/(.+)"

    def GET(self, jobpath):
        jl = jenkins.JenkinsAPI( server )
        job = jl.get_item( jobpath )
        rv = dict()
        for cfg in job.configurations():
            state = jl.get_properties( "%s/%s/lastBuild" % (job.path, cfg),
                          ["estimatedDuration", "duration", "result",
                              "building", "timestamp"] )
            rv[cfg] = state

        web.header("Content-Type", "application/json")
        meta = dict()
        meta["name"] = job.name();
        meta["path"] = job.path;
        meta["state"] = rv;
        print str(meta)
        return json.dumps(meta)




if __name__ == "__main__":
  app.run()
