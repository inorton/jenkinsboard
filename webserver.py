"""
jenkins visualisation board - inb@ncipher.com 2016
"""
#!/usr/bin/env python

import web
import json
import jenkins
import os

THISDIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_JSON = os.path.join(THISDIR, "settings.json")
SETTINGS = json.load(open(SETTINGS_JSON, "rb"))

GLOBALS = {}

app = web.auto_application()
render = web.template.render("templates/", base="master", globals=GLOBALS)


class index(app.page):
    """
    Main page.
    """
    path = '/'

    def GET(self):
        """
        Render
        :return:
        """
        boardname = SETTINGS["board"]
        return render.index(None, boardname)


class selected(app.page):
    """
    List the selected jobs
    """
    path = "/selected/(.+)"

    def GET(self, boardname):
        """
        Render
        :param boardname:
        :return:
        """
        jl = jenkins.JenkinsAPI(SETTINGS["master"])
        joblist = jl.get_all_jobs()
        web.header("Content-Type", "application/json")
        rv = []
        for jobitem in joblist:
            if not jobitem:
                continue
            if not jobitem.name():
                continue
            params = jl.get_properties(jobitem.path,
                                       ["actions[parameterDefinitions[*]]"])

            if "actions" in params:
                for pd in params["actions"]:
                    if "parameterDefinitions" in pd:
                        plist = pd["parameterDefinitions"]
                        for param in plist:
                            if "name" in param:
                                if param["name"] == "jenkinsboard":
                                    boards = param["description"].split(",")
                                    if boardname in boards:
                                        rv.append({
                                            "name": jobitem.name(),
                                            "configs": jobitem.configurations(),
                                            "path": jobitem.path,
                                            "link": SETTINGS["master"] + "/" + jobitem.path,
                                        })
        return json.dumps(rv)


class jobs(app.page):
    """
    All jobs
    """
    path = "/jobs/"

    def GET(self):
        """
        Render
        :return:
        """
        jl = jenkins.JenkinsAPI( SETTINGS["master"] )
        joblist = jl.get_all_jobs()
        web.header("Content-Type", "application/json")
        rv = []
        for jobitem in joblist:
            rv.append({
                "name": jobitem.name(),
                "path": jobitem.path,
                "configs": jobitem.configurations(),
                "link": SETTINGS["master"] + "/" + jobitem.path,
                })

        return json.dumps(rv)


class job(app.page):
    """
    Individual build
    """
    path = "/job/(.+)"

    def GET(self, jobpath):
        """
        Render
        :param jobpath:
        :return:
        """
        jl = jenkins.JenkinsAPI(SETTINGS["master"])
        jobitem = jl.get_item(jobpath)
        jobitem.url = "%s/%s" % (SETTINGS["master"], jobpath)
        web.header("Content-Type", "application/json")
        return json.dumps(jobitem.data)


class status(app.page):
    """
    Status page
    """
    path = "/status/(.+)"

    def GET(self, jobpath):
        """
        Render
        :param jobpath:
        :return:
        """
        jl = jenkins.JenkinsAPI(SETTINGS["master"])
        jobitem = jl.get_item(jobpath)
        rv = dict()
        for cfg in jobitem.configurations():
            state = jl.get_properties(
                "%s/%s/lastBuild" % (jobitem.path, cfg),
                ["estimatedDuration",
                 "duration", "result",
                 "building", "timestamp"])
            rv[cfg] = state

        web.header("Content-Type", "application/json")
        meta = dict()
        meta["name"] = jobitem.name()
        meta["path"] = jobitem.path
        meta["state"] = rv
        return json.dumps(meta)


if __name__ == "__main__":
  app.run()
