from google.cloud import datastore
import requests
import time
import json
import logging
import re


def register_user(request):
    body = {}
    response = {}
    try:
        data = request.get_json()
        if request.args:
            return json.dumps({'error': "Request mmissing parameters oneof ['email', 'name', 'password', 'gender', 'question', 'answer', instituteName']"}), 400, {'Content-Type': 'application/json'}
        if data:
            data_keys = data.keys()

            print('dict keys:')
            print(data_keys)

            if ('email' not in data_keys) or ('name' not in data_keys) or ('password' not in data_keys) or ('gender' not in data_keys) or ('question' not in data_keys) or ('answer' not in data_keys) or ('instituteName' not in data_keys):
                return json.dumps({'error': "Request mmissing parameters. Oneof ['email', 'name', 'password', 'gender', 'question', 'answer', instituteName']"}), 400, {'Content-Type': 'application/json'}

            email = data['email']
            question = data['question']
            answer = data['answer']
            name = data['name']
            gender = data['gender']
            instituteName = data['instituteName']
            password = data['password']
            print('data:')
            print(data)

            if (email == '') or (name == '') or (password == '') or (gender == '') or (answer == ''):
                return json.dumps({'error': "Request contains empty fields. Oneof ['email', 'name', 'password', 'gender', 'answer']"}), 400, {'Content-Type': 'application/json'}

            emailRegex = re.compile(
                '^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$')
            if emailRegex.match(email) == None:
                return json.dumps({'error': 'Invalid Email format!'}), 422, {'Content-Type': 'application/json'}

            passwordRegex = re.compile(
                '^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{8,})')
            if passwordRegex.match(password) == None:
                return json.dumps({'error': 'Password must contain: At least 1 uppercase, At least 1 lowercase, At least 1 special character, minimum length of 8'}), 422, {'Content-Type': 'application/json'}

            reqData = {"email": email, "name": name, "password": password,
                       "gender": gender, "instituteName": instituteName}

            # print(email,password, answer, question, name, instituteName)

            response = requests.post("https://jo4yxaeh95.execute-api.us-east-1.amazonaws.com/default/serverless-authentication",
                                     data=json.dumps(reqData), headers={'Content-Type': 'application/json', 'Accept': 'text/plain'})
            # time.sleep(5)
            if (response.status_code >= 400):
                return response.text, response.status_code, {'Content-Type': 'application/json'}
            print(response)
            logging.info(response.text)
            print(response.text)
            response = eval(response.text)
            if 'message' in list(response.keys()):
                try:
                    client = datastore.Client()
                    entity = datastore.Entity(key=client.key('user'))
                    entity.update(
                        {'email': email, 'question': question, 'answer': answer})
                    client.put(entity)
                    body['message'] = 'User registered successfully!'
                    return json.dumps(body), 200, {'Content-Type': 'application/json'}
                except Exception as e:
                    print("ERR:", str(e))
                    body['message'] = str(e)
                    print('first')
                    return json.dumps(body), 500, {'Content-Type': 'application/json'}
            else:
                body['message'] = response['error']
                print('ssecond')
                return json.dumps(body), 500, {'Content-Type': 'application/json'}
        else:
            body['message'] = ""
            print('third')
            return json.dumps(body), 500, {'Content-Type': 'application/json'}
    except Exception as e:
        print("ERR:", str(e))
        body['message'] = str(e)
        print('fourth')
        return json.dumps(body), 500, {'Content-Type': 'application/json'}
