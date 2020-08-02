from google.cloud import datastore
import json
import pymysql


def authenticate(req):
    host = 'database-1.cogkys8dvclp.us-east-1.rds.amazonaws.com'
    user = 'admin'
    password = '12345678'
    db = 'serverless'

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

    try:
        data = req.get_json()

        # check whether JSON data is present in the req object
        if data:
            print(data)

            # get a list keys in the data object
            data_keys = data.keys()

            print('dict keys:')
            print(data_keys)

            # check whether any required key is not sent from client side
            if ('email' not in data_keys) or ('question' not in data_keys) or ('answer' not in data_keys):
                res["error"] = "Request mmissing parameters. Oneof ['email', 'question', 'answer']"
                return (json.dumps(res), 400, headers)

            email = data['email']
            answer = data['answer']
            question = data['question']
            print(email, question, answer)

            # check whether security answer is empty
            if answer == '':
                res["error"] = "Request contains empty fields. Oneof ['answer']"
                return (json.dumps(res), 400, headers)

            # get GCP Datastore
            client = datastore.Client()
            query = client.query(kind='user')
            result = query.add_filter('email', '=', email).fetch(1)
            print(result)

            user = [dict(e) for i, e in enumerate(result)]

            if user:
                # match user's security question and answer
                if user[0]['question'] == question and user[0]['answer'] == answer:
                    res['message'] = 'User autenticated successfully!'

                    try:
                        # connect to RDS
                        connection = pymysql.connect(
                            host=host, user=user, password=password, db=db)
                        # update user's status to Online
                        with connection.cursor() as cursor:
                            query = 'UPDATE user set user.online = 1 where user.email = %s'
                            cursor.execute(query, email)
                            connection.commit()
                            print('User status changed to online')
                        connection.close()

                        print('User autenticate success')
                        return json.dumps(res), 200, headers

                    except Exception as e:
                        print(e)
                        res['error'] = str(e)
                        return json.dumps(res), 500, headers

                print('Security question and answer do not match!')
                res['error'] = 'Security question and answer do not match!'
                return json.dumps(res), 401, headers

            print('User not found')
            res['error'] = 'User not found'
            return json.dumps(res), 404, headers

        res['error'] = "Request missing parameters. Oneof ['answer', 'question', 'email']"
        return (json.dumps(res), 400, headers)

    except Exception as e:
        print(str(e))
        res['error'] = str(e)
        return (json.dumps(res), 500, headers)
