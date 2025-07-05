import pandas as pd
import matplotlib.pyplot as plt
import os

# Load usage data
df = pd.read_csv("data/processed/ec2_usage_summary.csv")
df["Timestamp"] = pd.to_datetime(df["Timestamp"])
df = df.sort_values("Timestamp")
df = df.fillna(0)

os.makedirs("reports", exist_ok=True)

# CPU Utilization Over Time
plt.figure(figsize=(12, 4))
plt.plot(df["Timestamp"], df["CPUUtilization"], color="blue", linewidth=1)
plt.title("EC2 CPU Utilization Over Time")
plt.xlabel("Time")
plt.ylabel("CPU Utilization (%)")
plt.grid(True)
plt.tight_layout()
plt.savefig("reports/cpu_usage_plot.png")
print("📊 Saved: reports/cpu_usage_plot.png")

# Cost Efficiency Comparison
# Constants from earlier analysis
avg_cpu = df["CPUUtilization"].mean()
total_hours = len(df) * (10 / 60)

t2_cost = round(total_hours * 0.0116, 4)
t3_cost = round(total_hours * 0.0208, 4)

efficiency_t2 = t2_cost / avg_cpu if avg_cpu > 0 else float("inf")
efficiency_t3 = t3_cost / avg_cpu if avg_cpu > 0 else float("inf")

# Bar plot
plt.figure(figsize=(6, 4))
bars = plt.bar(
    ["t2.micro", "t3.small"],
    [efficiency_t2, efficiency_t3],
    color=["green", "orange"]
)
plt.title("Cost per 1% Avg CPU Usage")
plt.ylabel("Cost in USD ($)")
plt.grid(axis="y")

for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, yval + 0.01, f"${yval:.2f}",
             ha='center', va='bottom')

plt.tight_layout()
plt.savefig("reports/cost_efficiency_comparison.png")
print("Saved: reports/cost_efficiency_comparison.png")
