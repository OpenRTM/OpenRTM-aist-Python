FROM ubuntu:20.04

COPY OpenRTM-aist-Python /root/OpenRTM-aist-Python

RUN apt update\
 && apt install -y --no-install-recommends\
 python3-pip\
 g++\
 ca-certificates\
 wget


RUN pip3 install pyflakes\
 && pip3 install --upgrade pyflakes


CMD cd /root/OpenRTM-aist-Python/\
 && pyflakes OpenRTM_aist/*.py\
 && pyflakes OpenRTM_aist/ext/http/HTTPTransport.py\
 && pyflakes OpenRTM_aist/ext/ssl/SSLTransport.py\
 && pyflakes OpenRTM_aist/ext/transport/OpenSplice/*.py\
 && pyflakes OpenRTM_aist/ext/transport/ROS2Transport/*.py\
 && pyflakes OpenRTM_aist/ext/transport/ROSTransport/*.py\
 && pyflakes OpenRTM_aist/ext/sdo/observer/ComponentObserverConsumer.py\
 && pyflakes OpenRTM_aist/ext/logger/fluentlogger/FluentLogger.py\
 && pyflakes OpenRTM_aist/ext/fsm4rtc_observer/ComponentObserverConsumer.py
