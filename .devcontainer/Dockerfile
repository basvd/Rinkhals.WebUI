FROM mcr.microsoft.com/devcontainers/base:trixie

ENV PIP_BREAK_SYSTEM_PACKAGES=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        micropython \
        python3-pip \
        curl \
        ca-certificates \
    && pip3 install --no-cache-dir hatch \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 24 LTS via nvm and enable Yarn globally through Corepack.
RUN su - vscode -c 'curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash \
    && . "$HOME/.nvm/nvm.sh" \
    && nvm install 24 \
    && corepack enable yarn'
