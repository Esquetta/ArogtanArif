from flask import  Flask
from threading import  Thread

app=Flask('')
@app.route("/")
def home():
    return "Hoşgeldin"

def run():
    app.run(host="0.0.0.0",port=8080)

def  live():
    t=Thread(target=run)
    t.start()