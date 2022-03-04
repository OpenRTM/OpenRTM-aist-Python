FROM ubuntu:20.04

COPY OpenRTM-aist-Python /root/OpenRTM-aist-Python

RUN apt update\
 && apt install -y --no-install-recommends\
 pip3\
 g++\
 ca-certificates\
 wget


RUN sudo pip3 install flake8\
 && sudo pip3 install --upgrade flake8


CMD cd /root/OpenRTM-aist-Python/\
 && pyflakes OpenRTM_aist/*.py --ignore="E501,E265,E402"\
 && pyflakes OpenRTM_aist/ext/http/HTTPTransport.py --ignore="E501,E265"\
 && pyflakes OpenRTM_aist/ext/ssl/SSLTransport.py --ignore="E501,E265"\
 && pyflakes OpenRTM_aist/ext/transport/OpenSplice/*.py --ignore="E501,E265"\
 && pyflakes OpenRTM_aist/ext/transport/ROS2Transport/*.py --ignore="E501,E265"\
 && pyflakes OpenRTM_aist/ext/transport/ROSTransport/*.py --ignore="E501,E265"\
 && pyflakes OpenRTM_aist/ext/sdo/observer/ComponentObserverConsumer.py --ignore="E501,E265"\
 && pyflakes OpenRTM_aist/ext/logger/fluentlogger/FluentLogger.py --ignore="E501,E265"\
 && pyflakes OpenRTM_aist/ext/fsm4rtc_observer/ComponentObserverConsumer.py --ignore="E501,E265"