FROM jupyter/scipy-notebook

LABEL maintainer="Drew Pellitieri <apellitieri@mitre.org>"

COPY LICENSE /LICENSE
COPY README.md /README.md

# FIXME: Local to MITRE only
# RUN wget -q -O - --no-check-certificate https://gitlab.mitre.org/mitre-scripts/mitre-pki/raw/master/os_scripts/install_certs.sh | MODE=alpine sh

USER root

WORKDIR /app
COPY . /app

# FIXME: bash and curl are for testing
#RUN apk add --no-cache \
#    python3 \
#    py3-pip \
#    openssl-dev \
#    bash \
#    curl

# RUN ln -s /usr/bin/python3 /usr/bin/python

#RUN apk add --no-cache --virtual .build-deps \
#    python3-dev

#RUN pip install setuptools wheel
RUN python -m pip install --upgrade pip
RUN pip install --upgrade -r requirements.txt

#RUN apk del --no-cache .build-deps && \
#    rm -fr /tmp/* /var/cache/apk/* /root/.cache/pip

#RUN adduser -D -H -h /app dotuser && \
#    chown -R dotuser:dotuser /app /var/log

RUN chown -R jovyan /app
RUN mkdir /app/.local
RUN chmod -R ugo+rwx /app

RUN mkdir -p /home/jovyan/.cache/matplotlib
RUN chmod -R ugo+rwx /home/jovyan
RUN chmod -R ugo+rwx /home/jovyan/.cache
RUN chmod -R ugo+rwx /home/jovyan/.cache/matplotlib

EXPOSE 8080
USER jovyan
ENV HOME /app

CMD jupyter notebook --port=8080 --ip='*' --NotebookApp.token='' --NotebookApp.password=''
