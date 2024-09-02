FROM ubuntu:24.04

RUN --mount=type=bind,target=/supra-host,source=system \
    --mount=type=cache,target=/var/lib/apt/lists \
    apt update && apt install -y --no-install-recommends \
    apt-transport-https \
    ca-certificates \
    \
    && apt update && apt upgrade -y \
    && apt install -y --no-install-recommends \
    openssl \
    python3 \
    python3-pip \
    adduser \
    \
    && pip install --break-system-packages -r /supra-host/requirements.txt \
    && adduser --disabled-password --gecos "" --uid 1711 supra \
    && echo "base done"

COPY bin supra/bin

ENTRYPOINT ["/supra/bin/entry.sh"]
