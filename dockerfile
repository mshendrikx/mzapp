# Use Ubuntu 22.04 base image
FROM ubuntu:22.04

# Update package lists
RUN apt update

# Install software
RUN apt install -y python3 python3-pip 

WORKDIR /app

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

RUN dpkg -i google-chrome-stable_current_amd64.deb

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

# Expose port 7005 for web traffic
EXPOSE 7005

# Start pyhton app in the foreground
CMD ["python3", "/app/app.py"]