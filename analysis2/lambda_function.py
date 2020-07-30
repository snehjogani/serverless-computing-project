import json
import boto3
import urllib.parse

aws_access_key_id="ASIASEGXGL67KO64JZWI"
aws_secret_access_key="WsJZ5r5q2GYvkW1gb1E7rmrLr2OX/KDMw4Lttb98"
aws_session_token="FwoGZXIvYXdzEGUaDN/jgOzSy12841bGHCK+AUE5Z7L/wrsvy0FEASihBOxspBRvAirVMygqANSAFJa7bzS1kVp+u9c+lj2FqdBxPRD/DuduNsAkpOT2/vQtRERK4UUVt7B7YH2TdpOu6gITWWqS7C1Vm+1yt5X7l3a/hz2OfEvBxJ8s3JfgS/pA+2cX1cBKWoElypts7naVAI7gmimt09pHzpvsxBJWXomzqxG8yCIK2FSFBXPtplWOMALOwZ8bxm8pgqNFfDW9jiShlfDPrcg7KjBH1m28W54ohKqH+QUyLU0bDWcA+xhG5IO9t00dj25SoFSKdV6MXisid9eAo1CBeTQ9+5+028SQ8n7TXA=="

s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    aws_session_token=aws_session_token)

comprehend = boto3.client(service_name='comprehend', aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              aws_session_token=aws_session_token)

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']

    #2 - Get the file/key name
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    #3 - Fetch the file from S3
    response = s3.get_object(Bucket=bucket, Key=key)

    #4 - Deserialize the file's cont    ent
    text = response["Body"].read().decode()
    
    text = json.loads(text)
    
    result = json.dumps(comprehend.detect_sentiment(Text=text['msg'], LanguageCode='en'), sort_keys=True, indent=4)
    result = json.loads(result)

    print(result,"--------------------")
    print(len(result))
    print(type(result))
    final = {"msg":text['msg'],"Sentiment":result['Sentiment'],"score":result['SentimentScore']}

    s3.put_object(Bucket='comprehandanalysis', Key=key, Body=json.dumps(final))

    print("done")
