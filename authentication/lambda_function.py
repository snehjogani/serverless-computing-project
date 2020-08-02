import json
import boto3
import botocore.exceptions
import hmac
import hashlib
import base64
import re
import os

COGNITO_APP_CLIENT_ID = os.environ.get('COGNITO_APP_CLIENT_ID')
COGNITO_APP_CLIENT_SECRET = os.environ.get('COGNITO_APP_CLIENT_SECRET')


def generate_hash(email):
    # Cognito secret hash generation function. Source: https://medium.com/@houzier.saurav/aws-cognito-with-python-6a2867dd02c6
    message = email + COGNITO_APP_CLIENT_ID
    digest = hmac.new(str(COGNITO_APP_CLIENT_SECRET).encode(
        'utf-8'), msg=str(message).encode('utf-8'), digestmod=hashlib.sha256).digest()
    secret_hash = base64.b64encode(digest).decode()
    return secret_hash


def lambda_handler(event, context):

    data = eval(event['body'])
    keys = data.keys()

    # check request body for email and password fields
    if ('email' not in keys) or ('password' not in keys):
        return {'statusCode': 400, 'body': json.dumps({'message': "Request missing parameters. Oneof ['email', 'password']"})}

    email = data['email']
    password = data['password']

    # check for empty fields
    if (email == '') or (password == ''):
        message = "Request contains empty fields. Oneof ['email', 'password']"
        return {'statusCode': 400, 'body': json.dumps({'message': message})}

    # validate email format
    emailRegex = re.compile(
        '^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$')
    if emailRegex.match(email) == None:
        return {'statusCode': 422, 'body': json.dumps({'message': 'Invalid Email format!'})}

    # validate password requirements
    passwordRegex = re.compile(
        '^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{8,})')
    if passwordRegex.match(password) == None:
        message = 'Password must contain: At least 1 uppercase, At least 1 lowercase, At least 1 special character, minimum length of 8'
        return {'statusCode': 422, 'body': json.dumps({'message': message})}

    try:
        client = boto3.client('cognito-idp')
        authenticate = {'USERNAME': email, 'PASSWORD': password,
                        "SECRET_HASH": generate_hash(email)}
        response = client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH', AuthParameters=authenticate, ClientId=COGNITO_APP_CLIENT_ID)
        print('response:', response)

        accessToken = response['AuthenticationResult']['AccessToken']
        userData = client.get_user(AccessToken=accessToken)

        # fetching user's email and security question
        user = {}
        for obj in userData['UserAttributes']:
            key = obj['Name']
            value = obj['Value']
            user[key] = value

        user = {'email': user['email'], 'question': user['custom:question']}
        return {'statusCode': 200, "body": json.dumps({'accessToken': accessToken, 'user': user})}

    except client.exceptions.NotAuthorizedException as e:
        print("client.exceptions.NotAuthorizedException:", str(e))
        return {'statusCode': 401, "body": json.dumps({'Error': str(e)})}

    except Exception as e:
        print("Error:", str(e))
        return {'statusCode': 500, "body": json.dumps({'Error': str(e)})}
