FROM python:3-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN apk add --update --no-cache mariadb-connector-c-dev \
        && apk add --no-cache --virtual .build-deps \
        mariadb-dev \
        gcc \
        musl-dev \
        libffi-dev \
        && pip install mysqlclient==1.4.6 \
        && pip install openstacksdk \ 
        && apk del .build-deps

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

EXPOSE 8080

CMD source admin-openrc.sh && python3 -m swagger_server
