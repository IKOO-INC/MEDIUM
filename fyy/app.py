from flask import Flask,redirect
from routes.admin import admin_bp
from routes.tracking import tracking_bp

app = Flask(__name__)

app.route('/')
def bsdchdf():
    return redirect('/tracking')

app.register_blueprint(admin_bp)
app.register_blueprint(tracking_bp)



if __name__ == "__main__":
    app.run(debug=True)