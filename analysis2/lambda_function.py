import json
import boto3
import urllib.parse

aws_access_key_id="ASIASEGXGL67D75UFZZW"
aws_secret_access_key="jCo+WwJdLqjUGLXXbdXdHTRQkdK+g6tqMkOFCEIq"
aws_session_token="FwoGZXIvYXdzEID//////////wEaDOPcpxUznlah3TimkyK+ARb/xiDsXuKJDqMIZWZF5wm0nZSBLRGyR5AkfFNCz4afkzZSIzYjoazoul2EjJ7zl04JQW8d1L9zDWSKSc0T4tM0iTGtIng7+OhMtKXS52Wph05tLKwMFK/8Fo7Ddvm6Qo3uQuM7idPQxFfVb0qUX6dtNC0ggZUV+LAqQpJQcVhZ6e1Wb/ADjH1KiBP7rkhWy3lRrMmgxhqwjlnjr4Jp+sBxR6+iLzKGZQ8ssDNtrycH0AhCdDSqEed2uZqpsmEo0I6N+QUyLdywdBrHJ98e25PNAk/kHZpYYILSZXsbsjOBTpvaOfAZUjoWjwqkyA5XCSKsvA=="
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
