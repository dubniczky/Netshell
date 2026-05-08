FROM python:3.12-slim

WORKDIR /app

# Install ping command
RUN apt update && \
    apt install -y iputils-ping

# Install packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install server
COPY . .
EXPOSE 8000


CMD ["python", "testserver.py"]
