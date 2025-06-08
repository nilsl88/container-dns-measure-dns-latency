import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import base64
from io import BytesIO
import sys

if len(sys.argv) != 3:
    print("Usage: python dns_plot_to_html.py <input_csv_file> <output_html_file>")
    sys.exit(1)

csv_path = sys.argv[1]
html_path = sys.argv[2]

# Load CSV
df = pd.read_csv(csv_path)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Round timestamps to the nearest minute
df['minute'] = df['timestamp'].dt.floor('min')

# Average over each minute, dns_server, and protocol
df_agg = (
    df.groupby(['minute', 'dns_server', 'protocol'])['query_time_ms']
      .mean()
      .reset_index()
)

# Color mapping
color_map = {
    ('8.8.8.8', 'udp'): 'orange',
    ('8.8.8.8', 'tcp'): 'red',
    ('1.1.1.1', 'udp'): 'green',
    ('1.1.1.1', 'tcp'): 'blue'
}

fig, ax = plt.subplots(figsize=(12, 7))
for (dns_server, protocol), group_data in df_agg.groupby(['dns_server', 'protocol']):
    label = f"{dns_server} ({protocol})"
    color = color_map.get((dns_server, protocol), None)
    ax.plot(group_data['minute'], group_data['query_time_ms'], marker='o', label=label, color=color)

# Format x-axis as "day/month HH:mm"
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M'))

fig.autofmt_xdate()  # Auto-rotate date labels

ax.set_title('DNS Query Time over Time by DNS Server and Protocol (Custom Colors)')
ax.set_xlabel('Time')
ax.set_ylabel('Average Query Time (ms)')
ax.legend(title='DNS Server (Protocol)', loc='upper right')
ax.grid(True)
plt.tight_layout()

# Save the plot as a base64-encoded PNG image
buffer = BytesIO()
plt.savefig(buffer, format='png')
buffer.seek(0)
img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
plt.close(fig)

# Write HTML with embedded image
html_content = f"""
<html>
<head>
    <meta charset="UTF-8">
    <title>DNS Query Time Visualization</title>
</head>
<body>
    <h2>DNS Query Time over Time by DNS Server and Protocol</h2>
    <img src="data:image/png;base64,{img_base64}" />
</body>
</html>
"""

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"HTML generated: {html_path}")

