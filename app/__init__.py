from flask import Flask
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from flask_bootstrap import Bootstrap
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

client = MongoClient(app.config['MONGO_URI'], server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client.pantry_tracker

Bootstrap(app)

from app import routes
