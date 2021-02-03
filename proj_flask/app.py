#this is where the main Flask app will reside
# where we write our function and URLs

# Step 1: import necessary libraries/modules

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy # this is to tell that we are using ORM
from sqlalchemy import func
from sqlalchemy import text
#import os
import csv


################################ our code begins here######################################################

# Step 02: initialize flask app here
app = Flask(__name__)
app.debug = True # we are not running app.py directly anymore, so must state explicitly here. Debug = True is for development purpose

#Step 03: add database configurations here
'''database_name, username, some_password are the things created in Ubuntu terminal
hostname can be replaced with localhost cuz it is setup on local machine, but when deployed to cloud, hostname can be different
default port used by Postgresql is 5432, it is the DB server port NOT the Flask app port
"postgresql:// username : some_password @ hostname : port / database_name " '''

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://exchinder_user:exchinder203@localhost:5432/exchinder_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db = SQLAlchemy(app)

# Step 04: import DB models
# import necessary data models (class)
from models import Student, University, group_chat_table # do it after DB configuration which is step 03

# Step 05: add routes and their binded functions here

@app.route('/PostIntRecord/', methods=['POST'])
def createIntRecord():
	telegram_chat_ID = request.json['telegram_chat_id']
	user_real_name = request.json['user_real_name']
	telegram_username = request.json['telegram_username']
	uni_name = request.json['uni_name']
	uni_country=request.json['uni_country']
	faculty=request.json['faculty']

	try:
		new_int_stu_record =Student(chat_id=telegram_chat_ID, name=user_real_name, tele_username=telegram_username,faculty=faculty)
		xuni=University.query.filter(University.country.ilike('%{}%'.format(uni_country))).filter(
			University.name.ilike('%{}%'.format(uni_name))).first()
		if xuni is None:
			return jsonify("No such university found! Please check again in the SMU Partner Uni lists on Oasis!")
		if xuni.grp_url is not None:
			new_int_stu_record.touni.append(xuni)
			db.session.add(new_int_stu_record) # add changes
			db.session.commit() # save changes by .commit()
			return jsonify(
				"A SMU group chat has been formed for this University.Please click on this link,{} to connect with your peers".format(
					xuni.grp_url))
		else:
			xmatch=Student.query.join(group_chat_table).join(University).filter(
			group_chat_table.c.stu_id==Student.id and group_chat_table.c.uni_id==University.id ).filter(
			xuni.name==University.name and xuni.country==University.country).first()
			new_int_stu_record.touni.append(xuni)
			db.session.add(new_int_stu_record) # add changes
			db.session.commit() # save changes by .commit()
			if xmatch is None:
				return jsonify("No matching record has been found. You will be notified once there is a match")
			else:
				return(xmatch.serialize())	
			
	except Exception as e:
		return (str(e))

@app.route('/getUniversities/', methods=['GET']) 
def get_universities():
	universities = University.query.order_by(University.name).all()
	return jsonify([uni.name for uni in universities])

@app.route('/getCountries/', methods=['GET']) 
def get_countries():
	output = []
	get_records = University.query.order_by(University.country).all()
	for r in get_records:
		if r.country not in output:
			output.append(r.country)
	return jsonify(output)


@app.route('/populateUniTable/', methods=['POST']) # This is to populate the University table with the records from the csv file.
def populateUniTable():
	with open('Partner_Universities_Overview_List_Fall_2020_1_converted.csv', 'r') as f:
		reader = csv.DictReader(f)
		try:
			for records in reader:
				uni_record = University(name=records['Partner University'], country=records['Country'])
				db.session.add(uni_record)
				db.session.commit()
			get_records = University.query.all()
			return jsonify([u.serialize() for u in get_records])
		except Exception as e:
			return (str(e))



@app.route('/updateurl/', methods=['PUT'])
def updateurl():
	if "Group_URL" in request.json and "University_ID" in request.json:
		try:
			grp_url = request.json['Group_URL']
			university_id = request.json['University_ID']
			get_uni = University.query.filter_by(id=university_id).first()
			get_uni.grp_url = grp_url
			db.session.commit()
			return jsonify("group_url is successfully updated",get_uni.serialize())
		except Exception as e:
			return (str(e))


@app.route('/getRecommendation/', methods=['GET'])
def get_Recommendation():
	if "faculty" in request.args:
		try:
			faculty = request.args['faculty']
			xrecords=University.query.with_entities(
				University.name,University.id,func.count(
					group_chat_table.c.stu_id).label('total')).join(group_chat_table).join(Student).filter(
			group_chat_table.c.stu_id==Student.id and group_chat_table.c.uni_id==University.id).filter(
			faculty==Student.faculty).group_by(University.id).order_by(text('total DESC')).limit(3).all()
			return jsonify([x for x in xrecords])
		except Exception as e:
			return (str(e))

			

#################################your code ends here######################################################

if __name__ == '__main__': # manage.py will be used to run the files
	app.run(debug=True)