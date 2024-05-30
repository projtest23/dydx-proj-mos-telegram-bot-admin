FROM python:3.10-slim-buster

# set a directory for the app
WORKDIR /usr/src/app

# copy all the files to the container
COPY . .

# install app-specific dependencies
RUN pip3 install  -r requirements.txt
RUN pip install python-telegram-bot[job-queue]

RUN chmod +x main.py

CMD python3 main.py;