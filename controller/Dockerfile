########
# BASE
########
ARG PYTHON_WHEEL_PATH=/var/cache/python/wheels
ARG WORKDIR_PATH=/workspaces
ARG EXECUTE_TESTS=false

########
# BUILDR
########
FROM python:3.10.9-slim-buster as builder-stage
ARG PYTHON_WHEEL_PATH
ARG WORKDIR_PATH
WORKDIR ${WORKDIR_PATH}
COPY ./requirements.txt . 
RUN apt-get -y update
RUN apt-get -y install make llvm-dev gcc python3-dev musl-dev
RUN pip install --upgrade pip
RUN pip wheel --wheel-dir ${PYTHON_WHEEL_PATH} -r requirements.txt

########
# TESTS
########
FROM python:3.10.9-slim-buster as tests-stage
ARG PYTHON_WHEEL_PATH
ARG WORKDIR_PATH
ARG EXECUTE_TESTS
WORKDIR ${WORKDIR_PATH}

COPY ./requirements.txt .
COPY --from=builder-stage ${PYTHON_WHEEL_PATH} ${PYTHON_WHEEL_PATH}
RUN apt-get -y update
RUN apt-get -y install make python3
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --no-index --find-links=${PYTHON_WHEEL_PATH} -r requirements.txt \
    && rm -rf ${PYTHON_WHEEL_PATH}

COPY . .
ADD "https://www.random.org/cgi-bin/randbyte?nbytes=10&format=h" skipcache
RUN if [ "${EXECUTE_TESTS}" = "true" ]; then echo "===> RUNNING TESTS"; export PYTHONPATH=$PYTHONPATH:$(pwd) && pytest .; fi

###############
# DEVCONTAINER
###############
FROM python:3.10.9-slim-buster AS devcontainer-stage
ARG PYTHON_WHEEL_PATH
ARG WORKDIR_PATH

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR ${WORKDIR_PATH}

COPY ./requirements.txt .
COPY --from=builder-stage ${PYTHON_WHEEL_PATH} ${PYTHON_WHEEL_PATH}
RUN apt-get -y update
RUN apt-get -y install make python3
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --no-index --find-links=${PYTHON_WHEEL_PATH} -r requirements.txt \
    && rm -rf ${PYTHON_WHEEL_PATH}

ARG USERNAME=unprivilegeduser
ARG USER_UID=1001
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME \
        && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

USER $USERNAME

###############
# EXECUTE
###############

FROM python:3.10.9-slim-buster AS execute-stage
ARG PYTHON_WHEEL_PATH
ARG WORKDIR_PATH

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR ${WORKDIR_PATH}

COPY ./requirements.txt .
COPY --from=builder-stage ${PYTHON_WHEEL_PATH} ${PYTHON_WHEEL_PATH}
RUN apt-get -y update
RUN apt-get -y install make python3
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --no-index --find-links=${PYTHON_WHEEL_PATH} -r requirements.txt \
    && rm -rf ${PYTHON_WHEEL_PATH}

COPY . .

RUN ls -la main.py
CMD python main.py -c config.yaml

