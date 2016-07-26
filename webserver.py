"""
jenkins visualisation board - inb@ncipher.com 2016
"""
#!/usr/bin/env python

import web
import json
import jenkins
import os
import settings


THISDIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_JSON = os.path.join(THISDIR, "settings.json")
SETTINGS = json.load(open(SETTINGS_JSON, "rb"))

GLOBALS = {}

app = web.auto_application()
render = web.template.render("templates/", base="master", globals=GLOBALS)


class admin(app.page):
    """
    The admin page
    """
    path = "/admin"

    def GET(self):
        """
        Render the admin page
        :return:
        """
        cfg = settings.get()
        jl = jenkins.JenkinsAPI(cfg["master"])
        jobs = jl.get_all_jobs()
        jobs = [ x.path for x in jobs if x.path and not x.jobs()]
        return render.admin(cfg, jobs)

    def POST(self):
        """
        Save settings
        :return:
        """
        inputs = web.input(jobs=[])

        cfg = settings.get()
        cfg["master"] = inputs.serveraddress
        cfg["jobs"] = inputs.jobs

        settings.set(cfg)

        return self.GET()


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
        return render.index(None)


class selected(app.page):
    """
    List the selected jobs
    """
    path = "/selected/"

    def GET(self):
        """
        Render
        :return:
        """

        jl = jenkins.JenkinsAPI(settings.get()["master"])
        jobs = settings.get()["jobs"]
        rv = []
        for job in jobs:
            jobitem = jl.get_item(job)
            assert jobitem
            rv.append({
                "name": jobitem.name(),
                "configs": jobitem.configurations(),
                "path": jobitem.path,
                "link": SETTINGS["master"] + "/" + jobitem.path,
            })

        web.header("Content-Type", "application/json")
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
        cfg = settings.get()
        joblist = cfg["jobs"]
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
