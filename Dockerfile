FROM python:3.12 AS final

EXPOSE 8080
WORKDIR /code
ENV START_THREADS=4
ENV BIND_INTERFACE=0.0.0.0
ENV BIND_PORT=8080
ENV LOG_LEVEL=info

RUN addgroup --gid 1000 user \
    && adduser --uid 1000 --gid 1000 --no-create-home user

HEALTHCHECK --interval=10s --timeout=9s CMD curl -f http://localhost/.diagnostics/health-ready || exit 1

# For layer caching grab only our reqs and install them...
COPY requirements.txt /code/requirements.txt

# Install any necessary system deps first
RUN apt-get update && \
    apt-get install -y curl=7.88.1-10+deb12u12 procps=2:4.0.2-3 --no-install-recommends && \
    pip install -r requirements.txt --no-cache-dir && \
    apt-get remove -y pkg-config build-essential && \
    apt-get autoremove -y && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*

# Copy our code which generally will be the only thing that changes in most updates
COPY src /code

USER user
ENTRYPOINT [ "/bin/sh", "-c", "uvicorn --workers=${START_THREADS} main:app --log-level ${LOG_LEVEL} --reload --host ${BIND_INTERFACE} --port ${BIND_PORT}"]

