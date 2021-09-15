FROM alpine:latest

LABEL maintainer="Drew Pellitieri <apellitieri@mitre.org>"

COPY LICENSE /LICENSE
COPY README.md /README.md

# FIXME: Local to MITRE only
# RUN wget -q -O - --no-check-certificate https://gitlab.mitre.org/mitre-scripts/mitre-pki/raw/master/os_scripts/install_certs.sh | MODE=alpine sh

WORKDIR /app

COPY . /app

# FIXME: bash and curl are for testing
RUN apk add --no-cache \
    python3 \
    py3-pip \
    openssl-dev \
    bash \
    curl

RUN ln -s /usr/bin/python3 /usr/bin/python

RUN apk add --no-cache --virtual .build-deps \
    python3-dev

RUN pip install setuptools wheel
RUN python -m pip install --upgrade pip
RUN pip install --upgrade -r requirements.txt

RUN apk del --no-cache .build-deps && \
    rm -fr /tmp/* /var/cache/apk/* /root/.cache/pip

RUN adduser -D -H -h /app dotuser && \
    chown -R dotuser:dotuser /app /var/log
USER dotuser
