import json
from models.user import User


def hello(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response


def  create(event, context):
    user = User()
    user.save()

    return {
        "statusCode" : 201
    }