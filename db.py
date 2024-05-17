from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi
uri = "mongodb+srv://mohamedamr2002a:9IfsisX1Tg861u5C@cluster0.mlzj0le.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri,tlsCAFile=certifi.where())

db=client.get_database("distributed_db")

logs_collection = db.get_collection("logs")

def insert_log(log_message):
    log_document = {'log': log_message}
    logs_collection.insert_one(log_document)

def view_logs():
    logs = logs_collection.find()
    for i, log in enumerate(logs):
        print(f"{i}:{log['log']}")
