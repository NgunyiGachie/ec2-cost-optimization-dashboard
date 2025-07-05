import os
import pandas as pd

#load usage data
df = pd.read_csv("data/processed/ec2_usage_summary.csv")
df["Timestamp"] = pd.to_datetime(df["Timestamp"])
df = df.sort_values("Timestamp")

#Fill missing values
df = df.fillna(0)

period_minutes = 10
total_hours = len(df) * (period_minutes / 60)

# CPU Utilization Analysis
avg_cpu = df["CPUUtilization"].mean()
underutilized = df[df["CPUUtilization"] < 10].shape[0]
underutilized_pct = (underutilized /len(df)) * 100

# Network Analysis
total_network_in = df["NetworkIn"].sum() / (1024 ** 2)
total_network_out = df["NetworkOut"].sum() / (1024 ** 2)
total_network = total_network_in + total_network_out

# Simulated Pricing
t2_micro_price = 0.0116 #USD/hr
t3_small_price = 0.0208 #USD/hr

t2_cost = round(total_hours * t2_micro_price, 4)
t3_cost = round(total_hours * t3_small_price, 4)

# Output Summary
print("\n=====EC2 Usage Efficiency Summary=====\n")
print(f"Total Monitoring Time : {round(total_hours, 2)} hours")
print(f"Average CPU Utilization : {round(avg_cpu, 2)}%")
print(f"Underutilized Time (<10%) : {round(underutilized_pct, 2)}% of runtime")

print(f"\nTotal Network In+Out : {round(total_network, 2)} MB")
print(f"   - Inbound: {round(total_network_in, 2)} MB")
print(f"   - Outbound: {round(total_network_out, 2)} MB")

print(f"\n Estimated Cost (if billed):")
print(f"   - t2.micro: ${t2_cost}")
print(f"   - t3.small: ${t3_cost}")

efficiency_t2 = t2_cost / avg_cpu if avg_cpu > 0 else float('inf')
efficiency_t3 = t3_cost / avg_cpu if avg_cpu > 0 else float('inf')
print(f"\n Cost per 1% CPU Usage:")
print(f"   - t2.micro: ${round(efficiency_t2, 4)} per 1% avg CPU")
print(f"   - t3.small: ${round(efficiency_t3, 4)} per 1% avg CPU")

os.makedirs("reports", exist_ok=True)

with open("reports/summary.txt", "w") as f:
    f.write("====== EC2 Usage Efficiency Summary ======\n\n")
    f.write(f"Total Runtime: {round(total_hours, 2)} hrs\n")
    f.write(f"Avg CPU Usage: {round(avg_cpu, 2)}%\n")
    f.write(f"Underutilized: {round(underutilized_pct, 2)}%\n")
    f.write(f"Total Network: {round(total_network, 2)} MB\n")
    f.write(f"Estimated Cost (t2.micro): ${t2_cost}\n")
    f.write(f"Estimated Cost (t3.small): ${t3_cost}\n")
    f.write(f"Cost/1% CPU (t2.micro): ${round(efficiency_t2, 4)}\n")
    f.write(f"Cost/1% CPU (t3.small): ${round(efficiency_t3, 4)}\n")

print("\n Summary also saved to: reports/summary.txt\n")