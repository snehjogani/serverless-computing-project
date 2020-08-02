from google.cloud import datastore
import requests
import time
import json
import logging
import re
import os


def register_user(req):
    res = {}
    headers = {}
    headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept, Authorization'
    headers['Access-Control-Allow-Origin'] = '*'
    headers['Access-Control-Allow-Methods'] = '*'
    headers['Access-Control-Max-Age'] = '3600'

    # handle OPTIONS request
    if req.method == 'OPTIONS':
        return ('', 204, headers)

    # Only allow HTTP POST request
    if req.method in ['GET', 'PUT', 'PATCH', 'DELETE']:
        res['error'] = 'Method not supported'
        return (json.dumps(res), 405, headers)

    headers['Access-Control-Max-Age'] = '1296000'
    headers['Content-Type'] = 'application/json'

    LAMBDA_FUNCTION_URI = os.environ.get('LAMBDA_FUNCTION_URI')

    try:
        data = req.get_json()

        # check whether JSON data is present in the req object
        if data:

            # get a list keys in the data object
            data_keys = data.keys()

            print('dict keys:')
            print(data_keys)

            # check whether any required key is not sent from client side
            if ('email' not in data_keys) or ('name' not in data_keys) or ('password' not in data_keys) or ('gender' not in data_keys) or ('question' not in data_keys) or ('answer' not in data_keys) or ('instituteName' not in data_keys):
                res["error"] = "Request mmissing parameters. Oneof ['email', 'name', 'password', 'gender', 'question', 'answer', instituteName']"
                return (json.dumps(res), 400, headers)

            email = data['email']
            question = data['question']
            answer = data['answer']
            name = data['name']
            gender = data['gender']
            instituteName = data['instituteName']
            password = data['password']
            print('data:')
            print(data)

            # check whether required fields are empty
            if (email == '') or (name == '') or (password == '') or (gender == '') or (answer == ''):
                res["error"] = "Request contains empty fields. Oneof ['email', 'name', 'password', 'gender', 'answer']"
                return (json.dumps(res), 400, headers)

            # email regex check
            emailRegex = re.compile(
                '^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$')
            if emailRegex.match(email) == None:
                res["error"] = 'Invalid Email format!'
                return (json.dumps(res), 422, headers)

            # password regex check
            passwordRegex = re.compile(
                '^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{8,})')
            if passwordRegex.match(password) == None:
                res["error"] = 'Password must contain: At least 1 uppercase, At least 1 lowercase, At least 1 special character, minimum length of 8'
                return (json.dumps(res), 422, headers)

            # print(email,password, answer, question, name, instituteName)

            # HTTP call to lambda function
            lambda_res = requests.post(LAMBDA_FUNCTION_URI, data=json.dumps({"email": email, "name": name, "password": password, "gender": gender, 'question': question, "instituteName": instituteName}), headers={
                'Content-Type': 'application/json', 'Accept': 'text/plain'})

            # lambda function response error handler
            if (lambda_res.status_code >= 400):
                return (lambda_res.text, lambda_res.status_code, headers)

            # lambda function response success handler
            if lambda_res.status_code == 200:
                try:
                    # add user email, security question & answer tupple to GCP datastore
                    client = datastore.Client()
                    entity = datastore.Entity(key=client.key('user'))
                    entity.update(
                        {'email': email, 'question': question, 'answer': answer})
                    client.put(entity)
                    res['message'] = 'User registered successfully!'
                    return (json.dumps(res), 200, headers)
                except Exception as e:
                    print("ERR:", str(e))
                    res['message'] = str(e)
                    print('first')
                    return (json.dumps(res), 500, headers)
            else:
                print('ssecond')
                res['message'] = lambda_res['error']
                return (json.dumps(res), 500, headers)
        else:
            res["error"] = "Request mmissing parameters oneof ['email', 'name', 'password', 'gender', 'question', 'answer', instituteName']"
            return (json.dumps(res), 400, headers)

    except Exception as e:
        print("ERR:", str(e))
        res['error'] = str(e)
        print('fourth')
        return (json.dumps(res), 500, headers)
