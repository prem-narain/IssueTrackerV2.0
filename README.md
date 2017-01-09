# Simple Issue Tracker V2.0
###########################################################################
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Design:System will have two models called User and Issue. With following information:

1. User:
        a. Email
        b. Username
        c. FirstName
        d. LastName
        e. Password
        f. AccessToken

2. Issue
        1. Title
        2. Description
        3. AssignedTo (User relation)
        4. Createdby (User relation)
        5. Status (Open, Closed)

Problem Statement:

Expose a RESTful API to make CRUD operation of Issue resource.
1. Every endpoint need user authentication
2. Authentication should be stateless (access_token)

#Install dependencies
$ virtualenv .pyenv
$ source .pyenv/bin/activate
$ pip install -r requirements.txt

#Run
$ python manage.py initdb
$ python manage.py runserver
* Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
* Restarting with stat

Now hit `http://localhost:5000/` to see the login

For Help:
$ python manage.py --help
usage: manage.py [-?] {shell,initdb,runserver} ...

positional arguments:
  {shell,initdb,runserver}
    shell               Runs a Python shell inside Flask application context.
    initdb
    runserver           Runs the Flask development server i.e. app.run()

optional arguments:
  -?, --help            show this help message and exit
