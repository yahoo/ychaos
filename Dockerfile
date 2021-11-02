FROM python:3.6-alpine
RUN apk --update add --virtual build-dependencies libffi-dev gcc musl-dev &&  pip install ychaos[chaos]