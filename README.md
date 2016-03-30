# JenkinsBoard
An auto-layout build feedback board for Jenkins

# Instructions
1. Clone the git repo
2. Edit settings.json to set your jenkins master with the FQDN of your jenkins server.
3. Start webserver.py (under a screen session?) Optionally adding a port number on the command line.

# Adding jobs to the view
1. Create a string parameter named "jenkinsboard" and set the _description_ to a value eg, "myproject"
2. Fire up a web browser and point it at the machine running webserver.py and go to http://WEBSERVER/myproject

# Multiple Boards
You can now have a job appear on several boards. The "jenkinsboard" parameter is
now taken as a comma separated list so you can have multiple boards and have jobs
appear on more than one of them.