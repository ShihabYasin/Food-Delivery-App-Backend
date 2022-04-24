FROM ubuntu:latest
SHELL ["/bin/bash", "-c"]
LABEL MAINTAINER="yasin"

# vars declaration section & basic dev lib setup
ENV GROUP_ID=1000 \
    USER_ID=1000 \
    BUILD_DEPS="build-essential python-dev" \
    APP_DEPS="python3-pip postgresql postgresql-contrib"

ARG FLASK_ENV="development"
ENV FLASK_ENV="${FLASK_ENV}" \
    PYTHONUNBUFFERED="true"

RUN apt-get update -y

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y ${BUILD_DEPS} ${APP_DEPS} #--no-install-recommends


RUN mkdir -p /opt/services/flaskapp/src
RUN mkdir -p /opt/services/flaskapp/static_files

WORKDIR /opt/services/flaskapp/src

ADD ./* /opt/services/flaskapp/src/
ADD static_files /opt/services/flaskapp/src/static_files/


RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Expose the Flask port
EXPOSE 9341

RUN chmod +x etl_run.sh run.sh

ENTRYPOINT ["./run_docker.sh"]