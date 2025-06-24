FROM python:3.11-slim

# Install system dependencies and security tools
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    nmap \
    dnsutils \
    && rm -rf /var/lib/apt/lists/*

# Install Go (needed for some tools)
RUN wget -O go.tar.gz https://go.dev/dl/go1.21.0.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go.tar.gz && \
    rm go.tar.gz

ENV PATH="/usr/local/go/bin:${PATH}"
ENV GOPATH="/go"
ENV GOBIN="/go/bin"

# Install security tools
RUN go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest && \
    go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest && \
    cp /go/bin/* /usr/local/bin/

# Update nuclei templates
RUN nuclei -update-templates

# Install testssl.sh
RUN git clone --depth 1 https://github.com/drwetter/testssl.sh.git /opt/testssl.sh && \
    ln -s /opt/testssl.sh/testssl.sh /usr/local/bin/testssl

# Create nmap-did-what directory
RUN mkdir -p /root/nmap-did-what/data

# Install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy scanner code
COPY . .

# Create scan results directory
RUN mkdir -p /app/scan_results

EXPOSE 5000

CMD ["python", "scanner.py"]
