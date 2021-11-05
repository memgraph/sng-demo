FROM python:3.7-slim-bullseye

# Install pymgclient
RUN apt-get update && \
    apt-get install -y git cmake make gcc g++ libssl-dev && \
    git clone --recursive https://github.com/memgraph/pymgclient /pymgclient && \
    cd pymgclient && \
    git checkout v1.1.0 && \
    python3 setup.py install && \
    python3 -c "import mgclient"

# Install poetry
RUN python3 -m pip install -U pip \
 && python3 -c "import urllib.request; print(urllib.request.urlopen('https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py').read().decode('utf-8'))" | python3

ENV PATH="${PATH}:/root/.poetry/bin"

WORKDIR /app
COPY poetry.lock pyproject.toml /app/

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

COPY . /app
EXPOSE 5000

ADD start.sh /
RUN chmod +x /start.sh

ENTRYPOINT [ "poetry", "run" ]
CMD ["/start.sh"]
