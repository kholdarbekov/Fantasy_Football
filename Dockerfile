# pull official base image
FROM python:3.7

# accept arguments
ARG PIP_REQUIREMENTS=production.txt

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip setuptools

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