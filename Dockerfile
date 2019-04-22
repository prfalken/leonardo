FROM ubuntu:14.04

RUN apt-get update

RUN apt-get install -y python3-pip git build-essential

WORKDIR /leonardo

ADD requirements.txt /leonardo/
RUN  pip install -r requirements.txt

ADD . /leonardo/

RUN mv config/leonardo.yaml.example config/leonardo.yaml
COPY sample/graphs/ /leonardo/graphs/

EXPOSE 5000

CMD ./run.py
