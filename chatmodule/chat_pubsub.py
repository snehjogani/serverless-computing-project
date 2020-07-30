from google.cloud import pubsub_v1
import os
from flask import Flask, request, jsonify
from google.cloud import pubsub_v1
import os
from gcloud import storage
import json
import datetime
import time

app = Flask(__name__)

os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"] = "/home/vishvesh/Documents/Dal/serverless/api-8566414966874230052-395627-4fca061a25a4.json"

project_id = "api-8566414966874230052-395627"

client = storage.Client()
bucket = client.get_bucket('publisher_files')


@app.route('/publish', methods=['GET', 'POST'])
def publish():
    topic_user = request.args.get('touser')
    sub_user = request.args.get('fromuser')
    subscription_id = sub_user

    msg = request.args.get('msg')

    topic_id = topic_user

    publisher = pubsub_v1.PublisherClient()
    topic_name = 'projects/{project_id}/topics/{topic}'.format(
        project_id=project_id,
        topic=topic_id,  # Set this to something appropriate.
    )
    try:
        pub = publisher.create_topic(topic_name)
        print("created pub", pub)
    except Exception as e:
        print(e,"------e------")
        pass

    subscriber = pubsub_v1.SubscriberClient()
    topic_name = 'projects/{project_id}/topics/{topic}'.format(
        project_id=project_id,
        topic=topic_id,
    )
    subscription_name = 'projects/{project_id}/subscriptions/{sub}'.format(
        project_id=project_id,
        sub=subscription_id,
    )

    try:
        sub = subscriber.create_subscription(
            name=subscription_name, topic=topic_name)
        print("created", sub)
    except Exception as e:
        print(e, "--------e----------")
        pass

    pub_msg = publisher.publish(topic_name, str.encode(msg))
    print("msg sent",pub_msg)
    data = {"msg": str(msg)}
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    name = topic_user + str(st)
    json.dump(data, open(name + ".json", 'w'))
    blob = bucket.blob(name + ".json")
    blob.upload_from_filename(name + ".json")
    blob.make_public()
    os.remove(name + ".json")

    return str(data)


# SUBSCRIBER
@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    topic_user = request.args.get('touser')
    sub_user = request.args.get('fromuser')

    topic_id = topic_user
    subscription_id = sub_user
    msg_list = []

    subscriber = pubsub_v1.SubscriberClient()
    # topic_name = 'projects/{project_id}/topics/{topic}'.format(
    #     project_id=project_id,
    #     topic=topic_id,
    # )
    subscription_name = 'projects/{project_id}/subscriptions/{sub}'.format(
        project_id=project_id,
        sub=subscription_id,  # Set this to something appropriate.
    )
    #
    # try:
    #     sub = subscriber.create_subscription(
    #         name=subscription_name, topic=topic_name)
    #     print("created", sub)
    # except Exception as e:
    #     print(e,"--------e----------")
    #     pass

    def callback(message):
        print(message.data)
        msg_list.append(message.data.decode('utf-8'))
        message.ack()

    future = subscriber.subscribe(subscription_name, callback)

    try:
        f = future.result(timeout=4.0)
        print(f,type(f))
    except Exception as e:
        future.cancel()
        pass

    # subscriber.close()

    return jsonify(msg_list)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0',
            port=int(os.environ.get(
                'PORT', 8080)))
