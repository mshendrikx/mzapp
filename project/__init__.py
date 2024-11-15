import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from apscheduler.schedulers.background import BackgroundScheduler

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

# init Background Scheduler 
scheduler = BackgroundScheduler()

def create_app():
    app = Flask(__name__)

    mariadb_pass = os.environ.get("MZDBPASS")
    mariadb_host = os.environ.get("MZDBHOST")
    mariadb_database = os.environ.get("MZDBNAME")

    app.config["SECRET_KEY"] = os.urandom(24).hex()
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "mysql+pymysql://root:" + mariadb_pass + "@" + mariadb_host + "/" + mariadb_database
    )

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    with app.app_context():
        
        # Create tables
        from .models import User, Mzcontrol
        db.create_all()

        mzcontrol = Mzcontrol.query.first()
        
        if not mzcontrol:
            new_mzcontrol = Mzcontrol(
                id='MZCONTROL',
                season = 0,
                deadline = 0,
            )
            db.session.add(new_mzcontrol)    
        # add admin user to the database
        user = User.query.filter_by(email="admin@mzapp.com").first()
        if not user:
            new_user = User(
                email="admin@mzapp.com",
                name="Administrator",
                password=generate_password_hash("Mz4pp", method="pbkdf2:sha256"),
                admin="X",
                mzuser=os.environ.get("MZUSER"),
                mzpass=os.environ.get("MZPASS"),
            )
            db.session.add(new_user)            
        
        # Control Data        
        check_updates(updateid=1)
        check_updates(updateid=2)

    @login_manager.user_loader
    def load_user(userid):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(userid)

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    return app

def check_updates(updateid):
    
    if updateid == 1:
        update_name = 'Control'
    elif updateid == 2:
        update_name = 'Countries'
    
    from .models import Updates
                
    update = Updates.query.filter_by(id=updateid).first()        
    if not update:
        new_update = Updates(
            id=updateid,
            name=update_name,
            minute='',
            hour='',
            dayofmonth='',
            month='',
            dayofweek='',
            function='',
            active=0,
        )
        db.session.add(new_update)
        db.session.commit()
    
