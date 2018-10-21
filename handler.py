import json
import os
import sys

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, "./vendored"))

import requests
import db
import neo4j_db

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

        if message.startswith("/start"):
            start(chat_id, first_name)
        elif message.startswith("/setOrigin"):
            origin = message.split("/setOrigin ", 1)[1]
            set_origin(chat_id, origin)
        elif message.startswith("/setDestination"):
            destination = message.split("/setDestination ", 1)[1]
            set_destination(chat_id, destination)
        elif message.startswith("/commute"):
            get_user_list(chat_id)
        elif message.startswith("/removeCommute"):
            remove_commute(passenger_id)
        elif message.startswith("/listall"):
            list_all_stations(chat_id)
        elif message.startswith("/listissues"):
            list_issues(chat_id)
        elif message.startswith("/list"):
            if message == "/list":
                list_lines(chat_id)
            else:
                line = message.split("/list ", 1)[1]
                list_stations_by_line(chat_id, line)
        elif message.startswith("/status"):
            if message == "/status":
                get_status_by_id(chat_id)
                return {"statusCode": 200}
            params = message.split(" ", 1)
            params = params[1].split("/", 1)
            if len(params) is 2:
                get_status(chat_id, params[0], params[1])
        else:
           help(chat_id)

    except Exception as e:
        print(e)

    return {"statusCode": 200}

def update(event, context):
    try:
        origin = event["origin"]
        destination = event["destination"]
        type = event["type"]
        message = None
        if 'message' in event:
            message = event["message"]

        if type == "add":
            neo4j_db.insert_error(origin, destination, message)
        elif type == "remove":
            neo4j_db.clear_error(origin, destination)
        else:
            return {"statusCode": 200}
    except Exception as e:
        print(e)

    return {
        "statusCode": 200,
        "origin": origin,
        "destination": destination,
        "type": type,
        "message": message
    }

def retrieve(event, context):
    try:
        origin = event["origin"]
        destination = event["destination"]
        type = event["type"]
        message = None
        if 'message' in event:
            message = event["message"]

        users = db.get_all_users()
        users_list = []

        for user in users:
            u_origin = user['origin']
            u_destination = user['destination']
            if neo4j_db.is_contained(u_origin, u_destination, origin, destination):
                users_list.append(user['userId'])

    except Exception as e:
        print(e)

    return {
        "statusCode": 200,
        "origin": origin,
        "destination": destination,
        "type": type,
        "message": message,
        "users": users_list
    }

def send_alert(event, context):
    try:
        origin = event["origin"]
        destination = event["destination"]
        type = event["type"]
        message = None
        if 'message' in event:
            message = event["message"]

        users = event["users"]

        response = ""

        if type == "remove":
            response += "I have some good news! The problem between {} and {} has been solved.".format(origin, destination)
        elif type == "add":
            response += "I am sorry to inform that there is an issue between {} and {} ".format(origin, destination)
            if message is not None:
                response += "({})".format(message)
            response += "."

        for user in users:
            data = {"text": response.encode("utf8"), "chat_id": user}
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

    if not neo4j_db.is_station(origin):
        response = "The station {} does not exist. Please insert a valid one.".format(origin)
    elif origin is not None and destination is not None:
        response = "You are set! You can list your defined locations using /commute!"
    elif destination is None:
        response = "Your origin has been recorded! Please set your destination using /setDestination <name>"

    data = {"text": response.encode("utf8"), "chat_id": passenger_id}
    db.update_passenger_origin(passenger_id, origin)
    requests.post(url, data)

def set_destination(passenger_id, destination):
    origin, curr_destination = db.get_user_info(passenger_id)

    if not neo4j_db.is_station(destination):
        response = "The station {} does not exist. Please insert a valid one.".format(destination)
    elif origin is not None and destination is not None:
        response = "You are set! You can list your defined locations using /commute!"
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

def get_status_by_id(passenger_id):
    origin, destination = db.get_user_info(passenger_id)
    response = ""

    if origin is None or destination is None:
        response += "Please set both origin and destination"
        data = {"text": response.encode("utf8"), "chat_id": passenger_id}
        requests.post(url, data)
        return {"statusCode": 200}

    error_list = neo4j_db.get_status_error_list(origin, destination)
    error_list = neo4j_db.get_status_error_list(origin, destination)
    #path = neo4j_db.get_shortest_path(origin, destination)
    #error_list = neo4j_db.get_error_list(path)

    if len(error_list) == 0:
        response += "Your commute is running smoothly. Enjoy!"
    elif len(error_list) == 1:
        response += "Unfortunately there is a problem on your regular commute.\n"
    elif len(error_list) == 2:
        response += "Damn, your commute has more than one problem!\n"

    for problem in error_list:
        origin = problem['origin']
        destination = problem['destination']
        message = problem['message']
        issue = "There is an issue between {} and {}: {}\n".format(origin, destination, message)
        response += issue


    data = {"text": response.encode("utf8"), "chat_id": passenger_id}
    requests.post(url, data)

def get_status(passenger_id, origin, destination):
    response = ""

    if not neo4j_db.is_station(origin) or not neo4j_db.is_station(destination):
        response += "Please set both valid origin and destination"
        data = {"text": response.encode("utf8"), "chat_id": passenger_id}
        requests.post(url, data)
        return {"statusCode": 200}


    path = neo4j_db.get_shortest_path(origin, destination)
    error_list = neo4j_db.get_error_list(path)

    if len(error_list) == 0:
        response += "This commute is running smoothly. Enjoy!"
    elif len(error_list) == 1:
        response += "Unfortunately there is a problem on this trip.\n"
    elif len(error_list) == 2:
        response += "There is more than one problem on this ride.\n"

    for problem in error_list:
        origin = problem['origin']
        destination = problem['destination']
        message = problem['message']
        issue = "There is an issue between {} and {}: {}\n".format(origin, destination, message)
        response += issue


    data = {"text": response.encode("utf8"), "chat_id": passenger_id}
    requests.post(url, data)

def list_all_stations(passenger_id):
    station_list = neo4j_db.list_stations()
    station_list.sort()
    response = 'List of every station in the network:\n' + '\n'.join(station_list)
    data = {"text": response.encode("utf8"), "chat_id": passenger_id}
    requests.post(url, data)

def list_lines(passenger_id):
    line_list = neo4j_db.list_lines()
    line_list.sort()
    response = 'List of lines in the network:\n' + '\n'.join(line_list) + '\nSend \'/list <line_name>\' to get the list of stations of a specific line.'
    data = {"text": response.encode("utf8"), "chat_id": passenger_id}
    requests.post(url, data)

def list_stations_by_line(passenger_id, line):
    station_list = neo4j_db.list_stations_by_line(line)
    station_list.sort()
    response = 'List of every station in the line {}:\n'.format(line) + '\n'.join(station_list)
    data = {"text": response.encode("utf8"), "chat_id": passenger_id}
    requests.post(url, data)

def list_issues(passenger_id):
    error_list = neo4j_db.list_issues()

    if len(error_list) == 0:
        response = 'No issues in the network.'
    else:
        response = 'Unfortunately, the network is facing some issues right now.\n'
        for problem in error_list:
            origin = problem['origin']
            destination = problem['destination']
            message = problem['message']
            issue = "There is an issue between {} and {}: {}\n".format(origin, destination, message)
            response += issue

    data = {"text": response.encode("utf8"), "chat_id": passenger_id}
    requests.post(url, data)

def remove_commute(passenger_id):
    db.erase_commute(passenger_id)
    response = 'Successfully erased your commute settings.'
    data = {"text": response.encode("utf8"), "chat_id": passenger_id}
    requests.post(url, data)

def help(passenger_id):
    response = 'Type /listall to list every station in the work\n\
                Type /list to list the lines in the network.\n\
                Type /list <line_name> to list every station in that line.\n\
                Type /setOrigin <station_name> to set the starting point of your regular commute.\n\
                Type /setDestination <station_name> to set the destination of your regular commute.\n\
                Type /commute to show the information on your regular commute.\n\
                Type /status to get information on the status and issues on your regular commute.\n\
                Type /status <origin_station_name>/<destination_station_name> to get information on the status and issues of a specific trip.\n\
                Type /listissues to list every issue in the network.\n\
                Type /clearCommute to clear information regarding your regular commute.\n'
    data = {"text": response.encode("utf8"), "chat_id": passenger_id}
    requests.post(url, data)

