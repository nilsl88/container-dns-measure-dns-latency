import sys
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def main():
    # 1. Check for command-line arguments
    if len(sys.argv) != 3:
        print("Usage: python dns_plot_with_custom_markers.py <input_csv_file> <output_html_file>")
        sys.exit(1)

    input_csv_path = sys.argv[1]
    output_html_path = sys.argv[2]

    try:
        # 2. Load and process the data using pandas
        df = pd.read_csv(input_csv_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['minute'] = df['timestamp'].dt.floor('min')

        # Aggregate data, including the 'domain'
        df_agg = (
            df.groupby(['minute', 'dns_server', 'protocol', 'domain'])['query_time_ms']
            .mean()
            .reset_index()
        )
        df_agg['label'] = df_agg['domain'] + " - " + df_agg['dns_server'] + " (" + df_agg['protocol'] + ")"
    except FileNotFoundError:
        print(f"Error: The file '{input_csv_path}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while processing the CSV file: {e}")
        sys.exit(1)

    # 3. Color and marker settings
    color_map = {
        '1.1.1.1': 'red',
        '8.8.8.8': 'blue'
    }
    marker_map = {
        '1.1.1.1': 's',   # Square
        '8.8.8.8': '^'    # Triangle
    }

    # 4. Plotting
    fig = plt.figure(figsize=(15, 10))
    for label, group in df_agg.groupby("label"):
        dns_server = group['dns_server'].iloc[0]
        color = color_map.get(dns_server, None)  # Default color if not specified
        marker = marker_map.get(dns_server, 'o') # Default marker if not specified
        plt.plot(group["minute"], group["query_time_ms"],
                 label=label,
                 marker=marker,
                 linewidth=1,
                 color=color)

    plt.title("DNS Query Time over Time by Domain, DNS Server, and Protocol", fontsize=16, fontweight='bold')
    plt.xlabel("Time")
    plt.ylabel("Average Query Time (ms)")
    plt.legend(loc="best", fontsize="small", ncol=2, title="Domain - DNS Server (Protocol)")
    plt.grid(True)
    plt.tight_layout()

    # 5. Save to buffer and create HTML
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close(fig)

    html_content = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>DNS Query Time Visualization</title>
        <style>
            body {{ font-family: sans-serif; margin: 2em; }}
            h2 {{ color: #333; }}
            img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; padding: 5px; }}
        </style>
    </head>
    <body>
        <h2>DNS Query Time over Time by Domain, DNS Server, and Protocol</h2>
        <img src="data:image/png;base64,{img_base64}" alt="DNS Query Time Plot" />
    </body>
    </html>
    """

    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ HTML report with custom markers successfully generated at: {output_html_path}")

if __name__ == '__main__':
    main()

