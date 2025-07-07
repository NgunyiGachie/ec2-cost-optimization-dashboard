import pandas as pd
import dash
from dash import html, dcc
import plotly.express as px
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(BASE_DIR, "scripts", "data", "processed", "ec2_usage_summary.csv")
df = pd.read_csv(data_path)
df["Timestamp"] = pd.to_datetime(df["Timestamp"])
df = df.fillna(0)
df = df.sort_values("Timestamp")

# Cost logic
period_minutes = 10
total_hours = len(df) * (period_minutes / 60)
avg_cpu = df["CPUUtilization"].mean()
t2_cost = round(total_hours * 0.0116, 4)
t3_cost = round(total_hours * 0.0208, 4)

# Dashboard
app = dash.Dash(__name__)
app.title = "EC2 Optimization Dashboard"

app.layout = html.Div(children=[
    html.H1("EC2 Instance Cost Optimization", style={"textAlign": "center"}),

    html.Div([
        html.H3("CPU Utilization Over Time"),
        dcc.Graph(figure=px.line(df, x="Timestamp", y="CPUUtilization",
                                 labels={"CPUUtilization": "CPU (%)"},
                                 title="CPU Utilization Over Time"))
    ]),

    html.Div([
        html.H3("Network In/Out (MB)"),
        dcc.Graph(figure=px.area(df, x="Timestamp", y=["NetworkIn", "NetworkOut"],
                                 labels={"value": "Bytes", "variable": "Direction"},
                                 title="Network Traffic Over Time"))
    ]),

    html.Div([
        html.H3("Cost Comparison"),
        dcc.Graph(figure=px.bar(
            x=["t2.micro", "t3.small"],
            y=[t2_cost, t3_cost],
            labels={"x": "Instance Type", "y": "Estimated Cost (USD)"},
            title="Estimated Cost Comparison"
        ))
    ]),

    html.Div([
        html.H4("🧾 Summary Metrics"),
        html.Ul([
            html.Li(f"Total Runtime: {round(total_hours, 2)} hours"),
            html.Li(f"Average CPU Utilization: {round(avg_cpu, 2)}%"),
            html.Li(f"Total Network: {round((df['NetworkIn'].sum() + df['NetworkOut'].sum()) / (1024**2), 2)} MB"),
            html.Li(f"Estimated t2.micro Cost (if billed): ${t2_cost}"),
            html.Li(f"Estimated t3.small Cost: ${t3_cost}")
        ])
    ])
])

if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get("PORT", 8050)),
        debug=True)
