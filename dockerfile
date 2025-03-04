FROM ubuntu:latest

RUN apt update
RUN apt install python3 python3-pip libgdal-dev -y

COPY . /CARST
WORKDIR /CARST
RUN pip3 install gdal==3.8.3 --break-system-packages
RUN pip3 install -r requirements.txt --break-system-packages
RUN pip3 install . --break-system-packages
RUN pip3 install --no-cache-dir --force-reinstall 'GDAL[numpy]==3.8.3' --break-system-packages
