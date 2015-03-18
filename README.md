# JenkinsBoard
A simple auto-layout build feedback board for Jenkins

# Instructions
1. Clone the git repo
2. Edit webserver.py to replace "triffid.ncipher.com" with the FQDN of your jenkins server
3. Start webserver.py (under a screen session?)

# Adding jobs to the view
1. Create a string parameter named "jenkinsboard" and set the _description_ to a value eg, "myproject"
2. Fire up a web browser and point it at the machine running webserver.py and go to http://WEBSERVER/myproject
