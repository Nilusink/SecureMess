# docker file for Server AND Client
FROM python:3.10.0

WORKDIR /usr/src/app/

# for superuser
RUN apt-get update -o Acquire::Check-Valid-Until=false -o Acquire::Check-Date=false \
  && apt-get install -y sudo

RUN adduser --disabled-password --gecos '' docker
RUN adduser docker sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER docker

# installing requirements
COPY ./core/ ./core/
COPY docker_config.json ./config.json
COPY ./requirements.txt ./

# for server
COPY ./Server.py ./

# for client
#COPY ./Client_noGUI.py ./

RUN sudo apt-get upgrade -y
RUN sudo apt-get install python-dev -y
RUN sudo pip install --no-cache-dir -r requirements.txt

# execute command
# for server
CMD [ "python", "./Server.py" ]

# for client
#CMD [ "python", "./Client_noGUI.py"]
