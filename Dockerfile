FROM python:3.7-slim-bullseye

# Install poetry
RUN pip install -U pip \
    && python -c "import requests; res=requests.get('https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py'); print(res.content)" | python
ENV PATH="${PATH}:/root/.poetry/bin"

# Install pymgclient
RUN apt-get update && \
    apt-get install -y git cmake make gcc g++ libssl-dev && \
    git clone --recursive https://github.com/memgraph/pymgclient /pymgclient && \
    cd pymgclient && \
    python3 setup.py install

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
