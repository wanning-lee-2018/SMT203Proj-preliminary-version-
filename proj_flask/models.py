# this is where all the database models (schema) will reside

import datetime

from app import db  # import db from our app.py file

########################## our code starts here #######################################

# this is done for ORM

group_chat_table = db.Table('grp_chat',
	db.Column('stu_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
	db.Column('uni_id', db.Integer, db.ForeignKey('university.id'), primary_key=True),
	db.Column('admin_username',db.String(80), unique=False, nullable=True)
)



class Student(db.Model):
	__tablename__ = 'student' #__tablename__ is an in-built variable
	# if we do not explicitly control the naming of our table, the tablename will get the class name

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80), unique=True, nullable=False)
	tele_username = db.Column(db.String(80), unique=True, nullable=False)
	chat_id=db.Column(db.Integer, unique=True, nullable=False)
	timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow,
	 onupdate=datetime.datetime.utcnow)
	faculty = db.Column(db.String(80),unique=False,nullable=False)
	# many-to-many model
	touni = db.relationship('University', secondary=group_chat_table,
	 back_populates='tostu', cascade='all', lazy=True)

	######## defining methods for the objects
	def __init__(self, name, tele_username,chat_id,faculty): # this is initialization, self is referring to the current object
		self.name = name
		self.tele_username = tele_username
		self.chat_id=chat_id
		self.faculty=faculty


	def __repr__(self): # representation, if I want to print object only, what do I print. Equivalent to print(object)
		return '<Student {} with id {} is created>'.format(self.name,self.id) # this will eventually be return to user when they post and this return statement is the result shown to them if the object is created successfully
		# return '[id {}, desc {}]'.format(self.id,self.desc)

	def serialize(self): # this must be in JSON format, which in python terms list/dict. convert single row in DB to a json object to user
		return{
			'id':self.id,
			'name':self.name,
			'tele_username':self.tele_username,
			#'chat_id':self.chat_id,
			'faculty':self.faculty,
			'confirmed_uni': [{"uni_id":log.id,"country":log.country ,"university":log.name,"grp_url":log.grp_url}for log in self.touni]
		}
	# dict in python is unordered, so the result may not follow id, desc, price sequence



class University(db.Model):
	_tablename__ = 'university' #__tablename__ is an in-built variable
	# if we do not explicitly control the naming of our table, the tablename will get the class name

	id = db.Column(db.Integer, primary_key=True, unique=True)
	name = db.Column(db.String(1000), unique=True, nullable=False)
	country=db.Column(db.String(80), unique=False, nullable=False)
	grp_url=db.Column(db.String(80), unique=False, nullable=True)
	timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow,
	 onupdate=datetime.datetime.utcnow)
	# many-to-many model
	tostu = db.relationship('Student', secondary=group_chat_table,
	 back_populates='touni'
	 #, cascade='all',lazy=True
	 )
######## defining methods for the objects
	def __init__(self, name,country): # this is initialization, self is referring to the current object
		self.name = name
		self.country = country
	


	def __repr__(self): # representation, if I want to print object only, what do I print. Equivalent to print(object)
		return '< University {} with id {} in country is created >'.format(self.name,self.id,self.country) # this will eventually be return to user when they post and this return statement is the result shown to them if the object is created successfully

	def serialize(self): # this must be in JSON format, which in python terms list/dict. convert single row in DB to a json object to user
		return{
			'id':self.id,
			'name':self.name,
			'country':self.country,
			'grp_url':[] if self.grp_url is None else self.grp_url
		}
	# dict in python is unordered, so the result may not follow this particular sequence



