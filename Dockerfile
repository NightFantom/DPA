# Base OS:
FROM ubuntu


# setting up OS:
RUN echo                                       \
  && apt-get update                            \
  && apt-get install -y dumb-init
  # dumb-init for writing easy entrypoints


# Setting up java:
RUN echo                                       \
  && apt-get install -y default-jre


# Setting up the python:
RUN echo                                       \
  && apt-get install -y python3-pip            \
  && pip3 install -U setuptools


# Copying files to container
COPY requirements.txt /
COPY src /src
COPY data /data
COPY histories /histories


# Installing requirements
RUN pip3 install -r ./requirements.txt


# Place where the platform stars to run (used "bash" for testing)
ENTRYPOINT ["/bin/bash"]