FROM python:3.7

# Install cmake
RUN apt-get update && \
    apt-get --yes install cmake

# Install poetry
RUN pip install -U pip \
    && curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
ENV PATH="${PATH}:/root/.poetry/bin"

# Install mgclient
RUN apt-get install -y git cmake make gcc g++ libssl-dev && \
    git clone https://github.com/memgraph/mgclient.git /mgclient && \
    cd mgclient && \
    git checkout 5ae69ea4774e9b525a2be0c9fc25fb83490f13bb && \
    mkdir build && \
    cd build && \
    cmake .. && \
    make && \
    make install

# Install pymgclient
RUN git clone https://github.com/memgraph/pymgclient /pymgclient && \
    cd pymgclient && \
    python3 setup.py build && \
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