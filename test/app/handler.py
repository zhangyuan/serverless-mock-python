import json
from models.user import User


def simple_get(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response


def simple_post(event, context):
    user = User()
    user.save()

    return {
        "statusCode" : 201
    }