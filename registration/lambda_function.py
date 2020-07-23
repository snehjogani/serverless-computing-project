import json
import pymysql
import pymysql.cursors
import sys
import hmac
import hashlib
import base64
import boto3
import botocore.exceptions

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
    try:
        connection = pymysql.connect(host='database-1.cogkys8dvclp.us-east-1.rds.amazonaws.com',
                                     user='admin', password='12345678', db='serverless', charset='utf8mb4')
    except Exception as e:
        print(e)
        return {"statusCode": 500, "body": json.dumps({'Error': "SQL Connection Error"})}

    data = eval(event['body'])

    email = data['email']
    name = data['name']
    password = data['password']
    gender = data['gender']
    instituteName = data['instituteName']

    # print(email, name, gender, password, instituteName)

    body = {}
    try:
        print('cognito request initiated')
        client = boto3.client('cognito-idp')
        client.sign_up(ClientId=COGNITO_APP_CLIENT_ID, SecretHash=get_secret_hash(email), Username=email, Password=password,  UserAttributes=[
            {'Name': "email", 'Value': email}, {'Name': 'name', 'Value': name}, {'Name': 'gender', 'Value': gender}], ValidationData=[{'Name': "email", 'Value': email}])
        print('cognito request completed')
    except client.exceptions.UsernameExistsException as e:
        print('client.exceptions.UsernameExistsException', str(e))
        body['error'] = "Cognito-Error" + "This username already exists"
        return {"statusCode": 409, "body": json.dumps(body)}
    except client.exceptions.InvalidPasswordException as e:
        print('client.exceptions.InvalidPasswordException', str(e))
        body['error'] = "Cognito-Error" + \
            "Password should have Caps, Special chars, Numbers"
        return {"statusCode": 422, "body": json.dumps(body)}
    except client.exceptions.UserLambdaValidationException as e:
        print('client.exceptions.UserLambdaValidationException', str(e))
        body['error'] = "Cognito-Error"+"Email already exists"
        return {"statusCode": 409, "body": json.dumps(body)}
    except Exception as e:
        print('Error', str(e))
        body['error'] = "Cognito-Error"+str(e)
        return {"statusCode": 500, "body": json.dumps(body)}
    else:
        try:
            print('inside try')
            with connection.cursor() as cursor:
                sql = "INSERT INTO `user` (`name`, `email`, `password`, `gender`, `instituteName`) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(
                    sql, (name, email, password, gender, instituteName))
                connection.commit()
                body["message"] = "Success"
            connection.close()
            return {"statusCode": 200, "body": json.dumps(body)}
        except Exception as e:
            body['error'] = "RDS: "+str(e)
            return {"statusCode": 500, "body": json.dumps(body)}
