import json
import boto3

client = boto3.client('iot-data', region_name='eu-central-1')

def lambda_handler(event, context):

    print(event)
    for entry in event:
        if entry.get("N") == "CpuUsage":
            cpu_usage = entry.get("V")
            break

    if cpu_usage is not None:
        output = {
            "request": {
                "namespace": "Greengrass",
                "metricData": {
                "metricName": "CpuUsage",
                "value": cpu_usage,
                "unit": "Percent"
                }
            }
        }
        response = client.publish(
            topic="cloudwatch/metric/put",
            qos=0,
            payload=json.dumps(output)
    
            )
        print(response)
    return {
        'statusCode': 200,
        'body': json.dumps('')
    }
