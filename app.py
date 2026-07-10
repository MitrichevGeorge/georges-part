from flask import Flask, session
from flask_session import Session
import redis
from routes import auth_bp, main_bp
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis.Redis(host='localhost', port=6379, db=0)


app.register_blueprint(main_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')

if __name__ == '__main__':
    app.run(debug=True)
