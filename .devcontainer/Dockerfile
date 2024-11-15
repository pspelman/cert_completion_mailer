FROM ubuntu:22.04 as base

ARG DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

LABEL author="Philip Spelman"

ARG NODE_VERSION='18.18.0'
ARG NVM_DIR=/root
ARG NVM_VERSION='v0.39.5'
ENV NODE_PATH $NVM_DIR/v$NODE_VERSION/lib/node_modules
ENV PATH $NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH

RUN apt-get update && \
    apt-get -y dist-upgrade && \
    apt-get -y autoremove && \
    apt-get clean all && \
    apt-get install -y \
    software-properties-common \
    git \
    curl \
    python3.11 \
    python3-pip \
    python3-dev \
    bash-completion \
    virtualenv \
    netcat \
    libreoffice

RUN curl -o- "https://raw.githubusercontent.com/nvm-sh/nvm/$NVM_VERSION/install.sh" | bash \
    && source $NVM_DIR/nvm.sh \
    && nvm install $NODE_VERSION

FROM base as builder
WORKDIR /install

COPY ./requirements.txt .
COPY requirements.txt /requirements.txt

RUN apt-get install -y python3-venv

ENV VIRTUAL_ENV=/home/workspace/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --upgrade pip \
    && pip install -r /requirements.txt --no-cache-dir

WORKDIR /home/workspace
COPY . /home/workspace

ENV PORT=8000
EXPOSE 8000

FROM base
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

ENV HOME=/home/workspace
ENV APP_HOME=/home/workspace
RUN mkdir -p $APP_HOME

WORKDIR $APP_HOME

COPY --from=builder /usr/local /usr/local
COPY --from=builder /home/workspace/ /home/workspace/
COPY --from=builder /home/workspace/requirements.txt .

RUN groupadd -g 1000 vscode \
    && useradd --uid 1000 --gid 1000 --shell /bin/bash --home-dir /home/workspace vscode \
    && echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers \
    && ln -s /usr/bin/python3.11 /usr/bin/python \
    && chown -R vscode:vscode /home/workspace \
    && adduser vscode sudo

ENV PIP_TARGET=/usr/local/pip-global
ENV PYTHONPATH=${PIP_TARGET}:${PYTHONPATH}
ENV PATH=${PIP_TARGET}/bin:${PATH}
RUN if ! cat /etc/group | grep -e "^pip-global:" > /dev/null 2>&1; then groupadd -r pip-global; fi \
    && usermod -a -G pip-global vscode \
    && umask 0002 && mkdir -p ${PIP_TARGET} \
    && chown :pip-global ${PIP_TARGET} \
    && ( [ ! -f "/etc/profile.d/00-restore-env.sh" ] || sed -i -e "s/export PATH=/export PATH=\/usr\/local\/pip-global:/" /etc/profile.d/00-restore-env.sh )

WORKDIR /
RUN echo 'PS1="\[\033[1;36m\]\u\[\033[1;36m\]@\[\033[1;36m\]\h:\[\033[1;352m\]\w\[\033[1;36m\]\$\[\033[0m\] "' >> /home/workspace/.bashrc

ENV TERM=xterm-256color
USER vscode

CMD ["python3 -m venv $VIRTUAL_ENV"]