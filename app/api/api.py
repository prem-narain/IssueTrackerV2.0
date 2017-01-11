"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""
from flask import Flask, render_template, request, redirect,jsonify, g,abort,make_response
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from api_setup import Base, User, Issue
from flask import Flask

from flask_mail import Mail, Message
import sched
import time

from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()


app = Flask(__name__)


mail = Mail(app)

engine = create_engine('sqlite:///issuewithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@auth.verify_password
def verify_password(username_or_token, password):
    
    user_id = User.verify_auth_token(username_or_token)
    if user_id:
        user = session.query(User).filter_by(id = user_id).one()
    else:
        user = session.query(User).filter_by(Username = username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


def mail_scheduler(sender_mail,receiver_mail,msg_body,msg_subject):
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(5, 1, send_mail, (sender_mail,receiver_mail,msg_body,msg_subject)) #mail send after 5 sec
    scheduler.run()


def send_mail(sender_mail,receiver_mail,msg_body,msg_subject):
    
	try:
		msg = Message(msg_subject,
		  sender=sender_mail,
		  recipients=[receiver_mail])
		msg.body = msg_body       
		mail.send(msg)
		return 'Mail sent!'
	except Exception, e:
		return(str(e)) 



#mailconfiguring
app.config.update(
	                     DEBUG=True,
	                     #EMAIL SETTING 
                         MAIL_SERVER='smtp.gmail.com',
                         MAIL_PORT=465,
                         MAIL_USE_SSL=True,
                         MAIL_USERNAME = 'your-gmail',
	                     MAIL_PASSWORD = 'your-gmail-password'
	              )
            


#This uri will be invoked to get token
@app.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})



#For creating user or getting list of users in db
@app.route('/')
@app.route('/users',methods=['GET','POST'])
def get_create_users():

    users = session.query(User).all()

    if request.method == 'GET':
        return jsonify(user = [i.serialize for i in users])

    elif request.method == 'POST':             
        email = request.json.get('email')
        username = request.json.get('username')
        firstname = request.json.get('firstname')
        lastname = request.json.get('lastname')
        password = request.json.get('password')
    
        #checking Unique email address and username
        emails_list=[user.Email for user in users]
        username_list=[user.Username for user in users]

        if email in emails_list:
            return jsonify({"result": "email already exist"})
        elif username in username_list:
            return jsonify({"result": "username already exist"})
        
        #Assuming that if all fields are provided then only user will be created
        if email and username and firstname and lastname and password:
            user=User(Email=email,Username=username,FirstName=firstname,LastName=lastname,Password=password)
            session.add(user)
            session.commit()
            return jsonify(user = user.serialize)
        else:
            return make_response("Please provide all fields",400)


 
#For creating  getting list of users in db      
@app.route('/issues')
def get_issue():
    if request.method == 'GET':
        issues = session.query(Issue).all()
        return jsonify(user = [i.serialize for i in issues])        
 
             
#For creating issue (post)     
@app.route('/issues/create',methods=['GET','POST'])
@auth.login_required
def create_issue():
    
    if request.method == 'POST':          
        title = request.json.get('title')
        description = request.json.get('description')
        assignedTo = request.json.get('assignedto')
        #createdby = request.json.get('createdby')
        status = request.json.get('status')

        #createdby attribute will take from authentication
        createdby =session.query(User).filter_by(Username = g.user.Username).one().id

        #Assuming that if all fields are provided then only issue will be created
        if title and description and assignedTo and createdby and status:
            issue=Issue(Title=title, Description = description,Status=status,AssignedTo=int(assignedTo) , Createdby=int(createdby))
            session.add(issue)
            session.commit() 

            #sending mail
            sender_mail=session.query(User).filter_by(Username = g.user.Username).one().Email
            #sender_pwd =session.query(User).filter_by(Username = g.user.Username).one().Password
            receiver_mail= session.query(User).filter_by(id =assignedTo).one().Email
            msg_body="Issue ID:"+str(issue.id)+" has been assigned to you .Please check."
            msg_subject="New Issue created"
            mail_scheduler(sender_mail,receiver_mail,msg_body,msg_subject)
            
            
            return jsonify(issue = issue.serialize)
        
        else:
            return make_response("Please provide all fields",400)    
    else:
        return make_response("Only POST method is allowed on this URI",405)
        
        

@app.route('/users/<int:id>',methods=['GET','PUT','DELETE'])
def modify_user(id):
    try:
        user = session.query(User).filter_by(id = id).one()
    except:
        abort(404)
        return jsonify({"result":"NO such User found"})
    if request.method == 'GET':
        return jsonify(user = user.serialize)
    elif request.method == 'PUT':
        #UPDATE A SPECIFIC USER based on id Username and ID  can not be changed       
        #update if corresponding fields are in body during request 
        email = request.json.get('email')
        if email:
            user.Email=email        

        firstname = request.json.get('firstname')
        if firstname:
            user.FirstName=firstname

        lastname = request.json.get('lastname')
        if lastname:
            user.LastName=lastname

        password = request.json.get('password') 
        if password:
            user.Password=password
        
        #committing update       
        session.commit() 
        return jsonify(user = user.serialize)

    elif request.method == 'DELETE':
        session.delete(user)
        session.commit()
        return jsonify({"result":"USER Deteled"})

@app.route('/issues/<int:id>',methods=['GET','PUT','DELETE'])
@auth.login_required
def modify_issue(id):
    try:
        issue = session.query(Issue).filter_by(id = id).one()
    except:
        return jsonify({"resut":"NO such Issue found"})
    #find who created the issue
    creator_id=issue.Createdby
    creator=session.query(User).filter_by(id = creator_id).one()

    if request.method == 'GET':
        #RETURN A SPECIFIC issue
        return jsonify(issue = issue.serialize)

    elif request.method == 'PUT':
       
        #unauthorized
        if not g.user.Username ==creator.Username:
            return jsonify({'result':"you are not authorized to edit this Issue"})
        else:
            #UPDATE A SPECIFIC issue based on id
            #createdby and id can not be changed           
            Title = request.json.get('title')
            if Title:
                issue.Title=Title

            Description = request.json.get('description')
            if Description:
                issue.Description=Description


            AssignedTo_old=issue.AssignedTo
            AssignedTo_new = request.json.get('assignedto')
            if (not AssignedTo_new) and(AssignedTo_old!=AssignedTo_new):
                issue.AssignedTo=AssignedTo


            Status = request.json.get('status')   
            if Status:
                issue.Status=Status
            
            #updating commit
            session.commit() 
            return jsonify(issue = issue.serialize)

    elif request.method == 'DELETE':
        if not g.user.Username ==creator.Username:
            return jsonify({'result':"you are not authorized to delete this Issue"})
        else:
            session.delete(issue)
            session.commit()
            return jsonify({"result":"issue Deteled"})



@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({ 'data': 'Hello, %s!' % g.user.Username })




if __name__ == '__main__':
    import os
    app.run(debug=True)
  