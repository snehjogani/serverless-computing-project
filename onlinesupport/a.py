import pymysql
import logging
import traceback
from os import environ
import json
// PyMsql used
endpoint='virtualhelper.cy3azzeijucd.us-east-1.rds.amazonaws.com'
port=3306
dbuser='admin'
password='123456789'
database='virtualhelper'


query="SELECT * FROM employees"

logger=logging.getLogger()
logger.setLevel(logging.INFO)

def make_connection():
    return pymysql.connect(host=endpoint, user=dbuser, passwd=password,
        port=int(port), db=database)

def log_err(errmsg):
    logger.error(errmsg)
    return {"body": errmsg , "headers": {}, "statusCode": 400,
        "isBase64Encoded":"false"}

logger.info("Cold start complete.") 


def lambda_handler(event,context):

    try:
        cnx = make_connection()
        cursor=cnx.cursor()
        
        try:
            cursor.execute(query)
        except:
            return log_err ("ERROR: Cannot execute cursor.\n{}".format(
                traceback.format_exc()))
        try:
            for result in cursor:
                if result[-1] == 'facebook':
                    return result[1]
            cursor.close()
        except:
            return log_err ("ERROR: Cannot retrieve query data.\n{}".format(
                traceback.format_exc()))


        return {"body": str(results_list), "headers": {}, "statusCode": 200,
        "isBase64Encoded":"false"}

    
    except:
        return log_err("ERROR: Cannot connect to database from handler.\n{}".format(
            traceback.format_exc()))


    finally:
        try:
            cnx.close()
        except: 
            pass 
