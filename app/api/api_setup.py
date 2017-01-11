from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)


import random, string

Base = declarative_base()

#secret_key which will become accesstoken after serializing
secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    Email = Column(String(50),unique=True)
    Username = Column(String(50),unique=True)
    FirstName=Column(String(50))
    LastName=Column(String(50))
    Password=Column(String(250))
    #AccessToken=Column(String(250)) 
    
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id':self.id,
            'Email': self.Email,
            'Username': self.Username,            
            'Password':self.Password
        }
    #This will create the token and dumps it with the "id" parameter of user which can be later verify by using loads method on "id"
    def generate_auth_token(self, expiration=600):
    	s = Serializer(secret_key, expires_in = expiration)
    	return s.dumps({'id': self.id })

    def verify_password(self, password):
        return self.Password==password

    #This method will take the token which we will provide and matches it with the user_id token which was dumped with the user_id
    @staticmethod #user will only be known once the token is decoded
    def verify_auth_token(token):
    	s = Serializer(secret_key)
    	try:
    		data = s.loads(token)
    	except SignatureExpired:
    		#Valid Token, but expired
    		return None
    	except BadSignature:
    		#Invalid Token
    		return None
    	user_id = data['id']
    	return user_id
 


class Issue(Base):
    __tablename__ = 'issue'

    id = Column(Integer, primary_key=True)
    Title = Column(String(50))
    Description = Column(String(50))
    AssignedTo=Column(Integer, ForeignKey('user.id'))
    Createdby=Column(Integer, ForeignKey('user.id'))
    Status=Column(String(10))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id':self.id,
            'Title': self.Title,            
            'AssignedTo':self.AssignedTo,
            'Createdby':self.Createdby,
            'status':self.Status,
            'Description':self.Description

        }



engine = create_engine('sqlite:///issuewithusers.db')


Base.metadata.create_all(engine)