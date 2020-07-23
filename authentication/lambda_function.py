import json
import boto3
import botocore.exceptions
import hmac
import hashlib
import base64
import re

COGNITO_USER_POOL_ID = 'us-east-1_LA97mUerk1'
COGNITO_APP_CLIENT_ID = '66abt1l96uq1io3mi46t4sbuc9'
COGNITO_APP_CLIENT_SECRET = 'jhd2t5lvo6voue7jbgoe0ur36ba7s33u5k9pd29g6ku1gip9hb4'


def get_secret_hash(username):
    msg = username + COGNITO_APP_CLIENT_ID
    dig = hmac.new(str(COGNITO_APP_CLIENT_SECRET).encode(
        'utf-8'), msg=str(msg).encode('utf-8'), digestmod=hashlib.sha256).digest()
    d2 = base64.b64encode(dig).decode()
    return d2


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
                        "SECRET_HASH": get_secret_hash(email)}
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
