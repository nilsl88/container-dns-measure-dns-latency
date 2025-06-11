import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import base64
from io import BytesIO
import sys

def main():
    """
    Generates an HTML file with an embedded plot of DNS query times,
    grouped by domain, DNS server, and protocol, using custom markers.
    """
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

    except FileNotFoundError:
        print(f"Error: The file '{input_csv_path}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while processing the CSV file: {e}")
        sys.exit(1)


    # 3. Define visualization styles
    # Colors for DNS servers
    color_map = {
        '8.8.8.8': 'red',
        '1.1.1.1': 'blue',
    }
    # Line styles for protocols
    linestyle_map = {
        'udp': '--',  # Dashed line for UDP
        'tcp': '-'    # Solid line for TCP
    }
    # === MODIFICATION START ===
    # Markers for DNS Servers as requested by the user
    marker_map = {
        '1.1.1.1': 's',           # 's' for square
        '8.8.8.8': '^',           # '^' for triangle
    }
    # === MODIFICATION END ===


    # 4. Create the plot
    fig, ax = plt.subplots(figsize=(16, 9))

    # Group by domain, server, and protocol to plot each combination
    for (domain, dns_server, protocol), group_data in df_agg.groupby(['domain', 'dns_server', 'protocol']):
        label = f"{domain} - {dns_server} ({protocol})"
        
        # Assign styles based on the maps
        color = color_map.get(dns_server, 'black')
        linestyle = linestyle_map.get(protocol, ':')
        # === MODIFICATION START ===
        # Assign marker based on the DNS server
        marker = marker_map.get(dns_server, 'x') # Default to 'x'
        # === MODIFICATION END ===

        ax.plot(group_data['minute'], group_data['query_time_ms'],
                marker=marker, # Apply the new marker
                linestyle=linestyle,
                color=color,
                label=label)

    # 5. Format the plot
    ax.set_title('DNS Query Time over Time by Domain, DNS Server, and Protocol')
    ax.set_xlabel('Time')
    ax.set_ylabel('Average Query Time (ms)')
    ax.grid(True)

    # Format the x-axis to display dates clearly
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M'))
    fig.autofmt_xdate()

    # Place legend outside the plot area for readability
    ax.legend(title='Domain - DNS Server (Protocol)', bbox_to_anchor=(1.04, 1), loc="upper left")
    
    # Adjust layout to make space for the legend
    plt.tight_layout(rect=[0, 0, 0.85, 1])


    # 6. Embed the plot into an HTML file
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
