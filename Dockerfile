# pull official base image
FROM ubuntu:20.04

# accept arguments
ARG PIP_REQUIREMENTS=production.txt
ARG DATABASE_NAME=dummy_db
ARG DATABASE_USER=dummy_user
ARG DATABASE_PASSWORD=dummy_password

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get -y upgrade

RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y python3-venv
RUN apt-get install -y lsb-release

# install dependencies
RUN pip3 install --upgrade pip setuptools

# install cron for scheduled tasks
RUN apt-get install -y cron

RUN apt -y install vim bash-completion wget

# Create the file repository configuration:
RUN sh -c 'echo "deb https://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
# Import the repository signing key:
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

RUN apt-get update
# Install the latest version of PostgreSQL.
RUN apt-get -y install postgresql-client-13

# create user for the Django project
RUN useradd -ms /bin/bash soccer

# set current user
USER soccer

# set work directory
WORKDIR /home/soccer

# create and activate virtual environment
RUN python3 -m venv venv

# copy and install pip requirements
COPY --chown=soccer ./requirements /home/soccer/requirements/
RUN ./venv/bin/pip3 install -r /home/soccer/requirements/${PIP_REQUIREMENTS}

# copy Django project files
COPY --chown=soccer . /home/soccer/

RUN sh -c 'echo "db:5432:${DATABASE_NAME}:${DATABASE_USER}:${DATABASE_PASSWORD}" > .pgpass'
RUN chmod 600 ~/.pgpass
RUN crontab crontab.txt