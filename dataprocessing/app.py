import os
import re
import boto3
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from flask import Flask
from stop_words import get_stop_words

app = Flask(__name__)

aws_access_key_id="ASIASEGXGL67HW5RF4PC"
aws_secret_access_key="GdcR51hBZ0cSfZhrxOuW5CHGsy8GeQw0/LvM8oOO"
aws_session_token="FwoGZXIvYXdzEEkaDKhYbl0ZAuXuGFW2YCK+Ac+cVernC4bOoEZH483yz6kKmyQ5loxR7LNJgjVCJSbTqN3J0TWDpCpUmKuHFHJ1gd5LhFWXBjjg7CrvG3VKbwaGRMM1OM4TWeVXni6B1xciQxxqfDNLmgnvdnfEid7jAC/XlFRD+osLEPbqNL1qPx/61qVaNIPORzmeUZ9s3CFwOzd9LTPHDCri8EsHzRY3LaWLzFmgwMenuhopXqF+hA+kd+KXgVGAgIqhNeHDtrMIO2sbUPHFQGKqSmIXCMUoyYKB+QUyLWLSQ46ACp1ykel1kMJe8QHnWBq7WbpbX7uMQZpSLnJIGyAbqg7nUTcuAxYIKw=="

s3 = boto3.resource('s3', aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    aws_session_token=aws_session_token)


def preprocess(text):
    # convert to lower case
    clean_str = text.lower()

    # remove usernames
    clean_str = re.sub('@[^\s]+', '', clean_str)

    # remove # in #hashtag
    clean_str = re.sub(r'#([^\s]+)', r'\1', clean_str)

    # remove emojis
    clean_str = clean_str.encode('ascii', 'ignore').decode('ascii')

    # remove URLs
    clean_str = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))', '', clean_str)
    clean_str = re.sub(r'http\S+', '', clean_str)

    # remove \n
    clean_str = clean_str.replace('\n', '')

    return str(clean_str.strip())

@app.route('/wordcloud')
def build_word_cloud():
    print("starting.....................")
    bucket = s3.Bucket('sourcedatab00853749')
    word_list = []
    for obj in bucket.objects.all():
        key = obj.key
        body = obj.get()['Body'].read()
        str_body = preprocess(body.decode("utf-8"))

        filtered_words = [word for word in str_body.split(" ") if word not in get_stop_words('english')]
        for word in filtered_words:
            if word.istitle:
                word_list.append(word)

    print("Done....................")
    wordcloud = WordCloud(width=1000, height=500).generate(" ".join(word_list))
    plt.figure(figsize=(15, 8))
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.savefig("wordcloud" + ".png", bbox_inches='tight')
    s3.meta.client.upload_file(Filename='wordcloud.png', Bucket='sampldatab00853749', Key='wordcloud.png',ExtraArgs={'ACL':'public-read'})
    return "https://sampldatab00853749.s3.amazonaws.com/wordcloud.png"

@app.route('/home')
def build_word_cl():
    return "working"

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0',
            port=int(os.environ.get(
                'PORT', 8080)))