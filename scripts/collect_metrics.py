import boto3
from datetime import datetime, timedelta
import pytz
import pandas as pd

# Setup AWS Clients

cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

INSTANCE_ID = 'i-021d5904228276358'

# Define time range (last 24 hours)

end_time = datetime.utcnow().replace(tzinfo=pytz.UTC)
start_time = end_time - timedelta(hours=24)

# Fetch CPUUtilization Metrics

response = cloudwatch.get_metrics_statistics(
    Namespace = 'AWS/EC2',
    MetricName = 'CPUUtilization',
    Dimensions = [
        {'Name': 'InstanceId', 'Value': INSTANCE_ID}
    ],
    StartTime=start_time,
    EndTime=end_time,
    Period=300,
    Statistics=['Average']
)

# Format Response

datapoints = response['Datapoints']
if not datapoints:
    print("No data found. Please enable monitoring in the instance running")
else:
    df = pd.DataFrame(datapoints)
    df = df.sort_values(by='Timestamp')
    df = df[['Timestamp', 'Average']]
    df.columns = ['Timestamp', 'CPUUtilization (%)']
    print(df)

    df.to_csv(f'data/processed/{INSTANCE_ID}_cpu_utitilization.csv', index=False)
    print(f"\nSaved to data/processed/{INSTANCE_ID}_cpu_utilization.csv")