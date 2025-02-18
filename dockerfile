FROM ubuntu:latest

RUN apt update
RUN apt install python3 python3-pip libgdal-dev -y
RUN pip3 install --no-cache-dir --force-reinstall 'GDAL[numpy]==3.6.2' --break-system-packages

COPY . /CARST
WORKDIR /CARST
RUN python3 -m pip install -r requirements.txt --break-system-packages
RUN python3 -m pip install . --break-system-packages