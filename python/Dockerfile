FROM python:3.11-slim

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    jq \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && apt-get autoclean -y \
    && rm -rf /var/cache/apt/archives /var/lib/apt/lists/* \
    ;

WORKDIR /app

COPY dist /app/dist

RUN make build
