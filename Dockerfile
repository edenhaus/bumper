ARG ARCH=amd64

FROM python:3.10-alpine

EXPOSE 443
EXPOSE 5223
EXPOSE 8007
EXPOSE 8883

COPY requirements.txt /requirements.txt

# install required python packages
RUN apk add git && pip3 install -r requirements.txt

WORKDIR /bumper

# Copy only required folders instead of all
COPY bumper/ bumper/

ENTRYPOINT ["python3", "-m", "bumper"]
