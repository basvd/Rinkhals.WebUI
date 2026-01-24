FROM mcr.microsoft.com/devcontainers/base:trixie

ENV PIP_BREAK_SYSTEM_PACKAGES=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends micropython python3-pip \
    && pip3 install --no-cache-dir hatch \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
