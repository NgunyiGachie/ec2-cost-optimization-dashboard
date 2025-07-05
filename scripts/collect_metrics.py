import boto3
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import pandas as pd
import pytz

# Load environment variables
load_dotenv()
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
region = os.getenv("AWS_DEFAULT_REGION")

# Instance ID
INSTANCE_ID = "i-021d5904228276358"

# Initialize CloudWatch client
cloudwatch = boto3.client(
    'cloudwatch',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    region_name=region
)

# Define the time range: last 7 days
end_time = datetime.utcnow().replace(tzinfo=pytz.UTC)
start_time = end_time - timedelta(days=7)

# Metrics to pull
metrics = {
    'CPUUtilization': 'Percent',
    'NetworkIn': 'Bytes',
    'NetworkOut': 'Bytes'
}

PERIOD = 600

def get_metric(metric_name):
    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName=metric_name,
        Dimensions=[
            {'Name': 'InstanceId', 'Value': INSTANCE_ID}
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=PERIOD,
        Statistics=['Average']
    )

    data = response['Datapoints']
    df = pd.DataFrame(data)
    if df.empty:
        print(f"No data found for {metric_name}")
        return pd.DataFrame()

    df = df[['Timestamp', 'Average']]
    df = df.sort_values(by='Timestamp')
    df = df.rename(columns={'Average': metric_name})
    return df

# Get each metric and merge on Timestamp
df_cpu = get_metric('CPUUtilization')
df_net_in = get_metric('NetworkIn')
df_net_out = get_metric('NetworkOut')

if df_cpu.empty and df_net_in.empty and df_net_out.empty:
    print("No metrics available. Make sure your instance has activity.")
else:
    dfs = [df_cpu, df_net_in, df_net_out]
    df_merged = dfs[0]
    for df in dfs[1:]:
        df_merged = pd.merge(df_merged, df, on='Timestamp', how='outer')

    df_merged = df_merged.sort_values(by='Timestamp')

    # Save merged data
    os.makedirs('data/processed', exist_ok=True)
    output_file = 'data/processed/ec2_usage_summary.csv'
    df_merged.to_csv(output_file, index=False)

    print(f"Usage metrics saved to: {output_file}")
    print(df_merged.head())
