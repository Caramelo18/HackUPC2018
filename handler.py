import json
import os
import sys

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, "./vendored"))

import requests
import db

TOKEN = os.environ['TELEGRAM_TOKEN']
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)
url = BASE_URL + "/sendMessage"


def hello(event, context):
    try:
        data = json.loads(event["body"])
        message = str(data["message"]["text"])
        chat_id = data["message"]["chat"]["id"]
        first_name = data["message"]["chat"]["first_name"]

        response = "Please /start, {}".format(first_name)

        #print(payload)

        if "start" in message:
            start(chat_id, first_name)
        elif "setOrigin" in message:
            origin = message.split("/setOrigin", 1)[1]
            set_origin(chat_id, origin)
        elif "setDestination" in message:
            destination = message.split("/setDestination", 1)[1]
            set_destination(chat_id, destination)
        elif "list" in message:
            get_user_list(chat_id)
        else:
            data = {"text": response.encode("utf8"), "chat_id": chat_id}
            requests.post(url, data)


    except Exception as e:
        print(e)

    return {"statusCode": 200}


def start(chat_id, first_name):
    response = " Hello {}! \n I am CommuBot and I am here to help you with your commute. To list the stations type /list. \n\n To set your starting point type /setOrigin <name>. \n\n To set your destination type /setDestination <name>".format(first_name)
    data = {"text": response.encode("utf8"), "chat_id": chat_id}

    requests.post(url, data)

def set_origin(passenger_id, origin):
    curr_origin, destination = db.get_user_info(passenger_id)

    if origin is not None and destination is not None:
        response = "You are set! You can list your defined locations using /list!"
    elif destination is None:
        response = "Your origin has been recorded! Please set your destination using /setDestination <name>"

    data = {"text": response.encode("utf8"), "chat_id": passenger_id}
    db.update_passenger_origin(passenger_id, origin)
    requests.post(url, data)

def set_destination(passenger_id, destination):
    origin, curr_destination = db.get_user_info(passenger_id)

    if origin is not None and destination is not None:
        response = "You are set! You can list your defined locations using /list!"
    elif origin is None:
        response = "Your destination has been recorded! Please set your origin using /setOrigin <name>"

    data = {"text": response.encode("utf8"), "chat_id": passenger_id}
    db.update_passenger_destination(passenger_id, destination)
    requests.post(url, data)

def get_user_list(passenger_id):
    origin, destination = db.get_user_info(passenger_id)
    response = ""

    if origin is not None and destination is not None:
        response += "Your current origin is {} and your destination is {}".format(origin, destination)
    elif origin is not None:
        response += "Your current origin is {}. However, you haven't defined a destination.".format(origin)
    elif destination is not None:
        response += "Your current destination is {}. However, you haven't defined an origin.".format(destination)
    else:
        response += "You haven't defined neither an origin nor a destination. Please specify one"

    data = {"text": response.encode("utf8"), "chat_id": passenger_id}
    requests.post(url, data)
