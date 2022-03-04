FROM ubuntu:20.04

COPY OpenRTM-aist-Python /root/OpenRTM-aist-Python

RUN apt update\
 && apt install -y --no-install-recommends\
 pip3\
 g++\
 ca-certificates\
 wget


RUN sudo pip3 install bandit\
 && sudo pip3 install --upgrade bandit


CMD cd /root/OpenRTM-aist-Python/\
 && bandit -r OpenRTM_aist
