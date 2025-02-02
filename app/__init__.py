from flask import Flask
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MONGO_URI'] = 'mongodb+srv://abdullahmusharaf200:60JMTqE3R2xhRQOz@pantrytracker.itc4lrd.mongodb.net/?retryWrites=true&w=majority&appName=pantryTracker'

client = MongoClient(app.config['MONGO_URI'], server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client.pantry_tracker

Bootstrap(app)

from app import routes