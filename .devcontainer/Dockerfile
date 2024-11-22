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
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:libreoffice/ppa && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y \
    git \
    curl \
    bash-completion \
    virtualenv \
    netcat \
    libreoffice \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip && \
    apt-get -y autoremove && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl -o- "https://raw.githubusercontent.com/nvm-sh/nvm/$NVM_VERSION/install.sh" | bash \
    && source $NVM_DIR/nvm.sh \
    && nvm install $NODE_VERSION

FROM base as builder
WORKDIR /install

COPY ./requirements.txt .
COPY requirements.txt /requirements.txt

ENV VIRTUAL_ENV=/home/workspace/venv
RUN python3.11 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip3 install --upgrade pip \
    && pip3 install -r /requirements.txt --no-cache-dir

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
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 \
    && update-alternatives --set python /usr/bin/python3.11 \
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

CMD ["python3.11", "-m", "venv", "$VIRTUAL_ENV"]