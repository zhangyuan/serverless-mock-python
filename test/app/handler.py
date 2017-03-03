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


def post_with_payload(event, context):
    return {
        "statusCode" : 200,
        "body" : event
    }


def post_with_payload_and_template(event, context):
    return {
        "statusCode" : 200,
        "body" : event
    }