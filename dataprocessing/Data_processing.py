import pandas as pd
import os
import re
import boto3
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from flask import Flask
app = Flask(__name__)

aws_access_key_id="ASIASEGXGL67NBJISADS"
aws_secret_access_key="AQPyEFmcpkLc6TnCMbmcG1CutAvHffSUYtdtoZQm"
aws_session_token="FwoGZXIvYXdzEJb//////////wEaDMyp8W7FNfVl7mc0TiK+ARsYpC4PkEHRupUFYLu2ZBMU37Q4OBErrcWpzHCVDg4nEqJOurGYhPEhCXOHG/d5TUfPBkoo1rOpDC/JJbu1BLsGa1P5vVdfutPCEye+MzeCfjB92dHeNeeNLOBekD5VVaepMk52rqo31SF3vwSvW9HKZzzL7ROImCjma22M5Mx6V9ix6qfRmeKu1V+Bcd5xfrJnRGIqk/v5tWI6ygTMz/jC3bu+Lpsbqlt3jygCGl1bADzuNSew63yRbsnzPvIoneLZ+AUyLb2mzDuFwhiSWbYa38zO+wT7Ttt43x8LUyQ7iwe3AFljFGR0NvknATHx59dqZg=="

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

@app.route('/')
def build_word_cloud():
    bucket = s3.Bucket('sourcedatab00853749')
    word_list = []
    for obj in bucket.objects.all():
        key = obj.key
        body = obj.get()['Body'].read()
        str_body = preprocess(body.decode("utf-8"))
        for word in str_body.split(" "):
            if word.istitle:
                word_list.append(word)

    wordcloud = WordCloud(width=1000, height=500).generate(" ".join(word_list))
    plt.figure(figsize=(15, 8))
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.savefig("wordcloud" + ".png", bbox_inches='tight')
    s3.meta.client.upload_file(Filename='wordcloud.png', Bucket='sampldatab00853749', Key='wordcloud.png',ExtraArgs={'ACL':'public-read'})
    return "https://sampldatab00853749.s3.amazonaws.com/wordcloud.png"


if __name__ == "__main__":
    app.run()