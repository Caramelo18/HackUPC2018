import json
import os
import sys

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, "./vendored"))

import requests

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

        if "start" in message:
            start(chat_id, first_name)
        elif "setStart" in message:
            setStart(chat_id, "Origin")
        elif "setDestination" in message:
            setDestination(chat_id, "Destination")
        else:
            data = {"text": response.encode("utf8"), "chat_id": chat_id}
            requests.post(url, data)


    except Exception as e:
        print(e)

    return {"statusCode": 200}


def start(chat_id, first_name):
    response = " Hello {}! \n I am CommuBot and I am here to help you with your commute. To list the stations type /list. \n\n To set your starting point type /setStart <name>. \n\n To set your destination type /setDestination <name>".format(first_name)
    data = {"text": response.encode("utf8"), "chat_id": chat_id}

    requests.post(url, data)

def setStart(passenger_id, origin):
    response = "Your origin has been recorded! Please set your destination using /setDestination <name>"
    data = {"text": response.encode("utf8"), "chat_id": passenger_id}

    requests.post(url, data)

def setDestination(passenger_id, destination):
    response = "You are set! You can list your defined locations using /list!"

    data = {"text": response.encode("utf8"), "chat_id": passenger_id}
    requests.post(url, data)
