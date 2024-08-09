FROM python:3.10.8-slim-buster

# Update and install git in a single layer
RUN apt update && \
    apt upgrade -y && \
    apt install -y git

# Copy the requirements file and install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip3 install -U pip && \
    pip3 install -U -r /requirements.txt

# Set up the working directory and copy the application code
WORKDIR /YNFILESBOT
COPY . /YNFILESBOT

# Define the command to run the application
CMD ["python3", "-m", "bot.main"]
