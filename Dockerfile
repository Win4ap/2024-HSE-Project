FROM python:latest

COPY ./server .
COPY ./requirements.txt .

RUN apt-get update \
 && apt-get install --no-install-recommends -y build-essential  git make gdb\
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN pip3.12 install -r requirements.txt
RUN pip install python-multipart
RUN pip install pysqlite3


CMD ["python3.12", "server.py"]