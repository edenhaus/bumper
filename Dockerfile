ARG ARCH=amd64

FROM $ARCH/python:3.7-alpine

COPY requirements.txt /requirements.txt

# install required python packages
RUN pip3 install -r requirements.txt

WORKDIR /bumper

# Copy only required folders instead of all
COPY bumper/ bumper/

ENTRYPOINT ["python3", "-m", "bumper"]
