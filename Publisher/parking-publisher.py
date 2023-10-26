import json
import boto3

client = boto3.client('iot-data', region_name='eu-central-1')

def lambda_handler(event, context):
    # TODO implement
    print(event)
    output_location = {
        "key":  "/greengrass/v2/new_test_gg_v2.png"
    }
    response = client.publish(
        topic="greengrass/v2/transformationcdk",
        qos=0,
        payload=json.dumps(output_location)

        )
    print(response)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
