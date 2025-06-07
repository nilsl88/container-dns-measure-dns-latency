FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y dnsutils && rm -rf /var/lib/apt/lists/*
COPY dns_query_time.sh .
COPY dns_plot_to_html.py .
COPY requirements.txt .
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "dns_plot_to_html.py"]
