FROM ubuntu:18.04

WORKDIR /app

COPY ./requirements.txt .

RUN apt-get -y update && \
    apt-get -y install python3 && \
    apt-get -y install python3-pip && \
    pip3 install -r requirements.txt && \
    rm requirements.txt

COPY ./Menu2Recipe .

CMD ["cd", "/app/Menu2Recipe"]
CMD ["python3", "Menu2Recipe.py","-n","麻婆豆腐","-t","1"]
