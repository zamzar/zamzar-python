ARG PYTHON_VERSION=3.7
FROM python:${PYTHON_VERSION}-bookworm

WORKDIR /usr/src/app

RUN pip install --upgrade build twine

COPY requirements.txt ./
COPY test-requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r test-requirements.txt

COPY . .