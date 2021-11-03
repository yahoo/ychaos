ARG PY_VERSION
FROM python:${PY_VERSION}-alpine
RUN apk --no-cache --update add --virtual build-dependencies libffi-dev gcc musl-dev && pip install ychaos[all]
