import json
import pymysql
import pymysql.cursors
import sys
import hmac
import hashlib
import base64
import boto3
import botocore.exceptions
import os

COGNITO_APP_CLIENT_ID = os.environ.get('COGNITO_APP_CLIENT_ID')
COGNITO_APP_CLIENT_SECRET = os.environ.get('COGNITO_APP_CLIENT_SECRET')
host = os.environ.get('host')
user = os.environ.get('user')
password = os.environ.get('password')
db = os.environ.get('db')


def generate_hash(email):
    # Cognito secret hash generation function. Source: https://medium.com/@houzier.saurav/aws-cognito-with-python-6a2867dd02c6
    message = email + COGNITO_APP_CLIENT_ID
    digest = hmac.new(str(COGNITO_APP_CLIENT_SECRET).encode(
        'utf-8'), msg=str(message).encode('utf-8'), digestmod=hashlib.sha256).digest()
    secret_hash = base64.b64encode(digest).decode()
    return secret_hash


def lambda_handler(event, context):
    try:
        # connect to RDS instance
        connection = pymysql.connect(
            host=host, user=user, password=password, db=db)
    except Exception as e:
        print(e)
        return {"statusCode": 500, "body": json.dumps({'Error': "SQL Connection Error"})}

    data = eval(event['body'])

    email = data['email']
    name = data['name']
    password = data['password']
    gender = data['gender']
    instituteName = data['instituteName']

    body = {}
    try:
        print('cognito request initiated')
        client = boto3.client('cognito-idp')
        # user sign up request for cognito user pool
        client.sign_up(ClientId=COGNITO_APP_CLIENT_ID, SecretHash=generate_hash(email), Username=email, Password=password,  UserAttributes=[
            {'Name': "email", 'Value': email}, {'Name': 'name', 'Value': name}, {'Name': 'gender', 'Value': gender}], ValidationData=[{'Name': "email", 'Value': email}])
        print('cognito request completed')

    # handle user already exists exception
    except client.exceptions.UsernameExistsException as e:
        print('client.exceptions.UsernameExistsException', str(e))
        body['error'] = "Cognito-Error" + "This username already exists"
        return {"statusCode": 409, "body": json.dumps(body)}

    except Exception as e:
        print('Error', str(e))
        body['error'] = "Cognito-Error"+str(e)
        return {"statusCode": 500, "body": json.dumps(body)}
    else:
        try:
            print('inside try')
            # insert user object into SQL table
            with connection.cursor() as cursor:
                sql = "INSERT INTO `user` (`name`, `email`, `password`, `gender`, `instituteName`) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(
                    sql, (name, email, password, gender, instituteName))
                connection.commit()
                body["message"] = "User registered successfully!"
            connection.close()
            return {"statusCode": 200, "body": json.dumps(body)}
        except Exception as e:
            body['error'] = "RDS: "+str(e)
            return {"statusCode": 500, "body": json.dumps(body)}
