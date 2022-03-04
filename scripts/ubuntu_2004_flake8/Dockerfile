FROM ubuntu:20.04

COPY OpenRTM-aist-Python /root/OpenRTM-aist-Python

RUN apt update\
 && apt install -y --no-install-recommends\
 python3-pip\
 g++\
 ca-certificates\
 wget


RUN pip3 install flake8\
 && pip3 install --upgrade flake8


CMD cd /root/OpenRTM-aist-Python/\
 && flake8 OpenRTM_aist/*.py\
 && flake8 OpenRTM_aist/ext/http/HTTPTransport.py\
 && flake8 OpenRTM_aist/ext/ssl/SSLTransport.py\
 && flake8 OpenRTM_aist/ext/transport/OpenSplice/*.py\
 && flake8 OpenRTM_aist/ext/transport/ROS2Transport/*.py\
 && flake8 OpenRTM_aist/ext/transport/ROSTransport/*.py\
 && flake8 OpenRTM_aist/ext/sdo/observer/ComponentObserverConsumer.py\
 && flake8 OpenRTM_aist/ext/logger/fluentlogger/FluentLogger.py\
 && flake8 OpenRTM_aist/ext/fsm4rtc_observer/ComponentObserverConsumer.py

