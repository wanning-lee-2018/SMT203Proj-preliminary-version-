# this handles all database migrations and manages the Flask app
from flask_script import Manager # manage Flask app
from flask_migrate import Migrate, MigrateCommand # manage DB

from app import app, db    # variables app and db are imported from app.py 

migrate = Migrate(app,db)  
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()