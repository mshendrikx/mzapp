import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from flask_apscheduler import APScheduler

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

def create_app():
    
    mariadb_pass = os.environ.get("MZDBPASS")
    mariadb_host = os.environ.get("MZDBHOST")
    mariadb_database = os.environ.get("MZDBNAME")

    app = Flask(__name__)
    
    scheduler = APScheduler()
    scheduler.init_app(app) 
    
    app.config["SECRET_KEY"] = os.urandom(24).hex()
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "mysql+pymysql://root:"
        + mariadb_pass
        + "@"
        + mariadb_host
        + "/"
        + mariadb_database
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
                id="MZCONTROL",
                season=0,
                deadline=0,
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

        # Background Jobs        
        from .models import Updates   
        check_updates(updateid=1)
        check_updates(updateid=2)
        updates = Updates.query.all()
        
        from .common import update_countries, control_data
        for update in updates:
            if update.active == 1:
                try:
                    id_str = str(update.id)
                    scheduler.add_job(
                        id=id_str,                  
                        func=update.function,
                        trigger='cron',
                        minute=update.minute,
                        hour=update.hour,
                        day=update.dayofmonth,
                        month=update.month,
                        day_of_week=update.dayofweek,
                        max_instances=1,
                    )
                except Exception as e:
                    print(e)                    
    
    scheduler.start()

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


def check_updates(updateid=0):

    if updateid == 1:
        update_name = "Control"
        update_function = "control_data"
    elif updateid == 2:
        update_name = "Countries"
        update_function = "update_countries"

    from .models import Updates

    update = Updates.query.filter_by(id=updateid).first()
    if not update:
        new_update = Updates(
            id=updateid,
            name=update_name,
            minute="*",
            hour="*",
            dayofmonth="*",
            month="*",
            dayofweek="*",
            function=update_function,
            active=0,
        )
        db.session.add(new_update)
        db.session.commit()
