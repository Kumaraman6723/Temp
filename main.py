from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from authlib.integrations.flask_client import OAuth
from config import appConf, SITE_KEY ,SECRET_KEY
from routes import register_routes


app = Flask(__name__)
app.config['SECRET_KEY'] = appConf.get("FLASK_SECRET")
Bootstrap5(app)
csrf = CSRFProtect(app)
oauth = OAuth(app)


oauth.register(
    "myApp",
    client_id=appConf.get("OAUTH2_CLIENT_ID"),
    client_secret=appConf.get("OAUTH2_CLIENT_SECRET"),
    server_metadata_url=appConf.get("OAUTH2_META_URL"),
    client_kwargs={
        "scope": "openid profile email https://www.googleapis.com/auth/user.birthday.read https://www.googleapis.com/auth/user.gender.read https://www.googleapis.com/auth/userinfo.profile"
    }
)


register_routes(app,oauth)

if __name__ == "__main__":
    app.run(debug=True, port=appConf.get("FLASK_PORT"))
