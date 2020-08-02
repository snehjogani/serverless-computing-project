import pymysql
import json
import os

host = os.environ.get('host')
user = os.environ.get('user')
password = os.environ.get('password')
db = os.environ.get('db')


def get_user_list(req):
    print('Function invoked')

    res = {}
    headers = {}
    headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept, Authorization'
    headers['Access-Control-Allow-Origin'] = '*'
    headers['Access-Control-Allow-Methods'] = '*'
    headers['Access-Control-Max-Age'] = '3600'

    print('method checked')
    if req.method in ['PUT', 'PATCH', 'DELETE']:
        res['error'] = 'Method not supported'
        return (json.dumps(res), 405, headers)

    headers['Access-Control-Max-Age'] = '1296000'
    headers['Content-Type'] = 'application/json'

    try:
        data = req.get_json()

        email = data['email']
        try:
            # connect to RDS instance
            connection = pymysql.connect(
                host=host, user=user, password=password, db=db)
            # fire get user list query
            with connection.cursor() as cursor:
                query = 'select email, name, online from user'
                cursor.execute(query)
                res['data'] = cursor.fetchall()

                print('data', res['data'])

            return json.dumps(res), 200, headers

        except Exception as e:
            print(e)
            res['error'] = str(e)
            return json.dumps(res), 500, headers

        finally:
            cursor.close()
            connection.close()

    except Exception as e:
        print(str(e))
        res['error'] = str(e)
        return (json.dumps(res), 500, headers)
