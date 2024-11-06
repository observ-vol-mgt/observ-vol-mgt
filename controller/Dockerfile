########
# BASE
########
ARG WORKDIR_PATH=/workspaces
ARG EXECUTE_TESTS=false
ARG EXECUTE_END2END_TESTS=false

########
# BUILDR
########
FROM python:3.10.9-slim-buster as builder-stage
ARG WORKDIR_PATH
WORKDIR ${WORKDIR_PATH}
COPY ./requirements.txt . 
RUN pip install --user -r requirements.txt

########
# TESTS
########
FROM python:3.10.9-slim-buster as tests-stage
ARG WORKDIR_PATH
ARG EXECUTE_TESTS
WORKDIR ${WORKDIR_PATH}
ENV PATH=/root/.local/bin:$PATH

COPY --from=builder-stage /root/.local /root/.local
COPY . .
COPY tests tests

ADD "https://www.random.org/cgi-bin/randbyte?nbytes=10&format=h" skipcache
RUN if [ "${EXECUTE_TESTS}" = "true" ]; then echo "===> RUNNING TESTS"; export PYTHONPATH=$PYTHONPATH:$(pwd) && pytest .; fi

########
# END2END TESTS
########
FROM python:3.10.9-slim-buster AS tests-end2end-stage
ARG WORKDIR_PATH
ARG EXECUTE_END2END_TESTS
WORKDIR ${WORKDIR_PATH}
ENV PATH=/root/.local/bin:$PATH

COPY --from=builder-stage /root/.local /root/.local
COPY . .

ADD "https://www.random.org/cgi-bin/randbyte?nbytes=10&format=h" skipcache
RUN if [ "${EXECUTE_END2END_TESTS}" = "true" ]; then echo "===> RUNNING END2END TESTS"; export PYTHONPATH=$PYTHONPATH:$(pwd) && python main.py -c config.yaml --noui; fi


###############
# DEVCONTAINER
###############
FROM python:3.10.9-slim-buster AS devcontainer-stage
ARG WORKDIR_PATH

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH=/root/.local/bin:$PATH

WORKDIR ${WORKDIR_PATH}

COPY --from=builder-stage /root/.local /root/.local
COPY . .

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
ARG WORKDIR_PATH

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH=/root/.local/bin:$PATH

WORKDIR ${WORKDIR_PATH}

COPY --from=builder-stage /root/.local /root/.local
COPY . .

CMD python main.py -c config.yaml

