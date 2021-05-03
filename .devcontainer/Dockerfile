# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.166.1/containers/python-3/.devcontainer/base.Dockerfile

# This is only for the development environment to facilitate VS Code / Docker integration
#ARG VARIANT=3
#FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}
FROM ubuntu:20.04 as base

# prevent interactive questions during installation
ARG DEBIAN_FRONTEND=noninteractive

# prevent from writing the pyc files - only makes sense if spawning python process one time
ENV PYTHONDONTWRITEBYTECODE 1
# prevents python from buffering the outputs
ENV PYTHONUNBUFFERED 1
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

LABEL author="Philip Spelman"

ARG NODE_VERSION='14.15.5'
ARG NVM_DIR=/root
ARG NVM_VERSION='v0.37.2'
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
	python3.9 \
    python3-pip \
    python3-dev \
    bash-completion \
    virtualenv \
    netcat && \
	add-apt-repository ppa:libreoffice/ppa && \
	apt-get update && \
    apt-get install -y \
	libreoffice

# Install NVM and desired version of Node
# [Option] Install Node.js
#ARG INSTALL_NODE="true"
#ARG NODE_VERSION="lts/*"
#RUN if [ "${INSTALL_NODE}" = "true" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi
#RUN adduser vscode \
#	&& adduser vscode sudo
# better way
#RUN useradd username \
#	&& useradd -g users -G sudo -s /bin/bash -m -c "Super McUser"  username


RUN curl -o- "https://raw.githubusercontent.com/nvm-sh/nvm/$NVM_VERSION/install.sh" | bash \
    && source $NVM_DIR/nvm.sh \
    && nvm install $NODE_VERSION


## Update args in docker-compose.yaml to set the UID/GID of the "vscode" user.
#ARG USER_UID=1000
#ARG USER_GID=$USER_UID
#RUN if [ "$USER_GID" != "1000" ] || [ "$USER_UID" != "1000" ]; then groupmod --gid $USER_GID vscode && usermod --uid $USER_UID --gid $USER_GID vscode; fi



###########
# BUILDER #
###########
FROM base as builder
WORKDIR /install
#COPY id_rsa /tmp/id_rsa

COPY ./requirements.txt .
COPY requirements.txt /requirements.txt
#RUN eval "$(ssh-agent -s)" \
#    && chmod 600 /tmp/id_rsa \
#    && ssh-add /tmp/id_rsa \
#    && mkdir -p /root/.ssh/ \
#    && touch /root/.ssh/known_hosts \
#    && ssh-keyscan bitbucket.org >> /root/.ssh/known_hosts \

RUN apt-get install -y \
	python3-venv

# Virtual Environment
ENV VIRTUAL_ENV=/home/workspace/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
COPY requirements.txt .
RUN pip install -r requirements.txt

RUN python3 -m pip install --upgrade pip \
    && python3 -m pip install -r /requirements.txt --no-cache-dir

WORKDIR /home/workspace
COPY . /home/workspace

ENV PORT=8000
EXPOSE 8000

# COPY ./start.sh /
# RUN chmod +x /start.sh

# COPY ./entrypoint.dev.sh /
# RUN chmod +x /entrypoint.dev.sh
# ENTRYPOINT ["/entrypoint.dev.sh"]


###############
# FINAL IMAGE #
###############
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
	&& useradd --uid 1000 --gid 1000 --shell /bin/sh --home-dir / vscode \
    && echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers \
    && ln -s /usr/bin/python3.9 /usr/bin/python \
	#&& chmod +x /home/workspace/private/* \
    #&& chmod +x /home/workspace/bin/* \
    #&& chmod +x /home/workspace/etc/* \
    #&& chmod +x /home/workspace/start.sh \
	#&& rm /home/workspace/id_rsa \
    && chown -R vscode:vscode /home/workspace \
    && adduser vscode sudo

# [Optional] Allow the vscode user to pip install globally w/o sudo
ENV PIP_TARGET=/usr/local/pip-global
ENV PYTHONPATH=${PIP_TARGET}:${PYTHONPATH}
ENV PATH=${PIP_TARGET}/bin:${PATH}
RUN if ! cat /etc/group | grep -e "^pip-global:" > /dev/null 2>&1; then groupadd -r pip-global; fi \
    && usermod -a -G pip-global vscode \
    && umask 0002 && mkdir -p ${PIP_TARGET} \
    && chown :pip-global ${PIP_TARGET} \
    && ( [ ! -f "/etc/profile.d/00-restore-env.sh" ] || sed -i -e "s/export PATH=/export PATH=\/usr\/local\/pip-global:/" /etc/profile.d/00-restore-env.sh )



#RUN groupadd -g 1000 vscode \
#RUN useradd --uid 1000 --gid 1000 --shell /bin/sh --home-dir /home/workspace vscode\
#RUN useradd --uid 1000 --gid 1000 --shell /bin/sh --home-dir / vscode\
#    && echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers \
#    && ln -s /usr/bin/python3.9 /usr/bin/python \
#    && chmod +x /home/workspace/private/* \
#    #&& chmod +x /home/workspace/bin/* \
#    #&& chmod +x /home/workspace/etc/* \
#    #&& chmod +x /home/workspace/start.sh \
#	#&& rm /home/workspace/id_rsa \
#    && chown -R vscode:vscode /home/workspace
#    && chown -R vscode:vscode /

# update the python path to make django-admin work correctly
#RUN export PYTHONPATH=$PYTHONPATH:/home/workspace/web/project_base

WORKDIR /
RUN echo 'PS1="\[\033[1;36m\]\u\[\033[1;36m\]@\[\033[1;36m\]\h:\[\033[1;352m\]\w\[\033[1;36m\]\$\[\033[0m\] "' >> ~/.bashrc

ENV TERM=xterm-256color
USER vscode

CMD ['python3 -m venv $VIRTUAL_ENV']
#ENV VIRTUAL_ENV=/opt/venv
#RUN python3 -m venv $VIRTUAL_ENV

#ENTRYPOINT ["/home/workspace/start.sh"]
