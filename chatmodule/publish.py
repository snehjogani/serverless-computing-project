from google.cloud import pubsub_v1
import os
from gcloud import storage
import json
import datetime
import time

os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"] = "/home/vishvesh/Documents/Dal/serverless/api-8566414966874230052-395627-4fca061a25a4.json"

project_id = "api-8566414966874230052-395627"
topic_id = "groupchat"
sub_id = "sub_grpchat"

client = storage.Client()
bucket = client.get_bucket('publisher_files')

# PUBLISHER
def publish(input):

    publisher = pubsub_v1.PublisherClient()
    topic_name = 'projects/{project_id}/topics/{topic}'.format(
        project_id=project_id,
        topic=topic_id,  # Set this to something appropriate.
    )
    # publisher.create_topic(topic_name)

    publisher.publish(topic_name, str.encode(input))
    data = {"msg":str(input)}
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    name = "vishvesh_" + str(st)
    json.dump(data, open(name + ".json", 'w'))
    blob = bucket.blob(name + ".json")
    blob.upload_from_filename(name + ".json")
    blob.make_public()
    os.remove(name + ".json")

if __name__ == "__main__":
    print("USER: Vishvesh | Status: online")
    while True:
        print()
        print("Enter msg:")
        input1 = input()
        publish(input1)
        print("msg sent")

