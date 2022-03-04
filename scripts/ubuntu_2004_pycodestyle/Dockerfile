FROM ubuntu:20.04

COPY OpenRTM-aist-Python /root/OpenRTM-aist-Python

RUN apt update\
 && apt install -y --no-install-recommends\
 python3-pip\
 g++\
 ca-certificates\
 wget


RUN pip3 install pycodestyle\
 && pip3 install --upgrade pycodestyle


CMD cd /root/OpenRTM-aist-Python/\
 && pycodestyle OpenRTM_aist/*.py --ignore="E501,E265,E402"\
 && pycodestyle OpenRTM_aist/ext/http/HTTPTransport.py --ignore="E501,E265"\
 && pycodestyle OpenRTM_aist/ext/ssl/SSLTransport.py --ignore="E501,E265"\
 && pycodestyle OpenRTM_aist/ext/transport/OpenSplice/*.py --ignore="E501,E265"\
 && pycodestyle OpenRTM_aist/ext/transport/ROS2Transport/*.py --ignore="E501,E265"\
 && pycodestyle OpenRTM_aist/ext/transport/ROSTransport/*.py --ignore="E501,E265"\
 && pycodestyle OpenRTM_aist/ext/sdo/observer/ComponentObserverConsumer.py --ignore="E501,E265"\
 && pycodestyle OpenRTM_aist/ext/logger/fluentlogger/FluentLogger.py --ignore="E501,E265"\
 && pycodestyle OpenRTM_aist/ext/fsm4rtc_observer/ComponentObserverConsumer.py --ignore="E501,E265"
