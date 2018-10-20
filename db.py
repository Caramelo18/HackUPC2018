import boto3
import os
dynamodb = boto3.resource('dynamodb')

def add_passenger_origin(userId, origin):
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    item = {
        'userId': str(userId),
        'origin': origin,
    }

    # write the todo to the database
    table.put_item(Item=item)

def add_passenger_destination(userId, destination):
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    item = {
        'userId': str(userId),
        'destination': destination,
    }

    # write the todo to the database
    table.put_item(Item=item)

def update_passenger_origin(userId, origin):
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    result = table.update_item(
        Key={
            'userId': str(userId)
        },
        UpdateExpression="set origin=:o",
        ExpressionAttributeValues={
            ":o": origin
        })

def update_passenger_destination(userId, destination):
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    result = table.update_item(
        Key={
            'userId': str(userId)
        },
        UpdateExpression="set destination=:d",
        ExpressionAttributeValues={
            ":d": destination
        })

def get_user_info(userId):
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    result = table.get_item(
        Key={
            'userId': str(userId)
        }
    )

    if 'Item' not in result:
        return None, None

    result = result['Item']

    if 'origin' not in result:
        return None, result['destination']
    elif 'destination' not in result:
        return result['origin'], None

    return result['origin'], result['destination']

def erase_commute(userId):
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    table.delete_item(
        Key={
            'userId': userId
        }
    )

def get_all_users():
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    result = table.scan()

    return result['Items']
