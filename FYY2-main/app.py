from flask import Flask,redirect, render_template
from routes.admin import admin_bp
from routes.tracking import tracking_bp
from routes.chat import chat_bp
app = Flask(__name__)

app.route('/')
def bsdchdf():
    return render_template('landing.html')

app.register_blueprint(admin_bp)
app.register_blueprint(tracking_bp)
app.register_blueprint(chat_bp)


if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)
