from flask import Flask,redirect, render_template, send_from_directory
app = Flask(__name__)

@app.route('/')
def bsdchdf():
    return send_from_directory('static','ru.png', as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)
