from google.cloud import pubsub_v1
import os
from flask import Flask
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
topic_id = "groupchat"
sub_id = "sub_grpchat"


client = storage.Client()
bucket = client.get_bucket('publisher_files')

@app.route('/publish')
def publish():

    publisher = pubsub_v1.PublisherClient()
    topic_name = 'projects/{project_id}/topics/{topic}'.format(
        project_id=project_id,
        topic=topic_id,  # Set this to something appropriate.
    )
    # publisher.create_topic(topic_name)

    publisher.publish(topic_name, str.encode("input"))
    data = {"msg":str("input")}
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    name = "vishvesh_" + str(st)
    json.dump(data, open(name + ".json", 'w'))
    blob = bucket.blob(name + ".json")
    blob.upload_from_filename(name + ".json")
    blob.make_public()
    os.remove(name + ".json")

    return str(data)

# SUBSCRIBER
@app.route('/subscribe')
def subscribe():
    subscriber = pubsub_v1.SubscriberClient()
    topic_name = 'projects/{project_id}/topics/{topic}'.format(
        project_id=project_id,
        topic=topic_id,
    )
    subscription_name = 'projects/{project_id}/subscriptions/{sub}'.format(
        project_id=project_id,
        sub=sub_id,
    )

    subscription_path = subscriber.subscription_path(project_id, sub_id)
    response = subscriber.pull(subscription_path, max_messages=5)

    for msg in response.received_messages:
        print("Received message:", msg.message.data)

    return str(response)

    # subscriber.create_subscription(
    #     name=subscription_name, topic=topic_name)

    # def callback(message):
    #     print()
    #     print(str(message.data))
    #     # message.ack()
    #     return str(message.data)
    #
    # future = subscriber.subscribe(subscription_name, callback)
    # # try:
    # z = future.result()
    # print(z,"---")
    # # except KeyboardInterrupt:
    # #     future.cancel()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0',
            port=int(os.environ.get(
                'PORT', 8080)))