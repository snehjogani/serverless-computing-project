import json
import boto3
import urllib.parse

aws_access_key_id="ASIASEGXGL67NB3GHDFM"
aws_secret_access_key="yrTBeOMdkQVcq1x53+6jV3vfM+9CNegVdPtt/mfz"
aws_session_token="FwoGZXIvYXdzEEsaDEkASh+L6K2/86hHIyK+AQFM5AanNBDG91H89v5f92zndwJWEPs9ArMsgbA8HF/GkZVaDr0p9j//r5CSBZjkz07rlYHvi8pIIHxqfKTOepCVkbBa7uWclkghEtJTnHV3xbMMesUfh1vHFzhXXcDR/ujozLcS6E8sRdxVAdxS0utXBkxHKCpfWTGE+X11WBVCwDKuo+7s+gmEoCOduXGH5PWsRC1ihm0Hn5eZSg0NmJLw9hrrJAPrN/XjcZv7Dh+ArSlJoofbTPDHPj8J5Pcorr6B+QUyLbgPeU9CH8DywetC4kOHn5ELppzUaALbSy8+wMQdXeeAsGcMItTSwmubV7Oj0w=="

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

    s3.put_object(Bucket='comprehandanalysis', Key=key, Body=str(final))

    print("done")
