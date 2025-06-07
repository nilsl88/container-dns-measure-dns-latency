import pandas as pd
import matplotlib.pyplot as plt
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

# Resample to average per minute
df_resampled = (
    df.set_index('timestamp')
      .groupby(['dns_server', 'protocol'])
      .resample('min')
      .mean(numeric_only=True)
      .reset_index()
)

# Color mapping
color_map = {
    ('8.8.8.8', 'udp'): 'black',
    ('8.8.8.8', 'tcp'): 'grey',
    ('1.1.1.1', 'udp'): 'brown',
    ('1.1.1.1', 'tcp'): 'magenta'
}

# Plot
fig, ax = plt.subplots(figsize=(12, 7))
for (dns_server, protocol), group_data in df_resampled.groupby(['dns_server', 'protocol']):
    label = f"{dns_server} ({protocol})"
    color = color_map.get((dns_server, protocol), None)
    ax.plot(group_data['timestamp'], group_data['query_time_ms'], marker='o', label=label, color=color)

ax.set_title('DNS Query Time over Time by DNS Server and Protocol (Custom Colors)')
ax.set_xlabel('Time')
ax.set_ylabel('Average Query Time (ms)')
ax.legend(title='DNS Server (Protocol)', loc='upper right')
ax.grid(True)
plt.tight_layout()

# Save the plot as an image and encode it to base64
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
