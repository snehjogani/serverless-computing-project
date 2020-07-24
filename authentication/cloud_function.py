from google.cloud import datastore
import json


def authenticate(request):
    body = {}
    headers = {
        'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept, Authorization',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': '*',
        'Access-Control-Max-Age': '3600'
    }

    if request.method == 'OPTIONS':
        return ('', 204, headers)

    if request.method in ['GET', 'PUT', 'PATCH', 'DELETE']:
        body['error'] = 'Method not supported'
        return (json.dumps(body), 405, headers)

    headers['Access-Control-Max-Age'] = '1296000'
    headers['Content-Type'] = 'application/json'

    try:
        data = request.get_json()

        if data:
            print(data)

            data_keys = data.keys()

            print('dict keys:')
            print(data_keys)

            if ('email' not in data_keys) or ('question' not in data_keys) or ('answer' not in data_keys):
                body["error"] = "Request mmissing parameters. Oneof ['email', 'question', 'answer']"
                return (json.dumps(body), 400, headers)

            email = data['email']
            answer = data['answer']
            question = data['question']
            print(email, question, answer)

            if answer == '':
                body["error"] = "Request contains empty fields. Oneof ['answer']"
                return (json.dumps(body), 400, headers)

            client = datastore.Client()
            query = client.query(kind='user')
            result = query.add_filter('email', '=', email).fetch(1)
            print(result)

            user = [dict(e) for i, e in enumerate(result)]

            if user:
                if user[0]['question'] == question and user[0]['answer'] == answer:
                    body['message'] = 'User autenticated successfully!'
                    print('User autenticate success')
                    return json.dumps(body), 200, headers

                print('Security question and answer do not match!')
                body['error'] = 'Security question and answer do not match!'
                return json.dumps(body), 401, headers

            print('User not found')
            body['error'] = 'User not found'
            return json.dumps(body), 404, headers

        body['error'] = "Request missing parameters. Oneof ['answer', 'question', 'email']"
        return (json.dumps(body), 400, headers)

    except Exception as e:
        print(str(e))
        body['error'] = str(e)
        return (json.dumps(body), 500, headers)
