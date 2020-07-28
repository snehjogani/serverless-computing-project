from google.cloud import pubsub_v1
import os

os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"] = "/home/vishvesh/Documents/Dal/serverless/api-8566414966874230052-395627-4fca061a25a4.json"

project_id = "api-8566414966874230052-395627"
topic_id = "groupchat"
sub_id = "sub_grpchat"

# SUBSCRIBER
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
    # subscriber.create_subscription(
    #     name=subscription_name, topic=topic_name)

    def callback(message):
        print(message.data)
        message.ack()

    future = subscriber.subscribe(subscription_name, callback)
    try:
        future.result()
    except KeyboardInterrupt:
        future.cancel()

if __name__ == "__main__":
    subscribe()
