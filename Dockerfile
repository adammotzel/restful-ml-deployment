FROM python:3.12.8-slim

WORKDIR /app

# install Git (needed for pip to install from git repos)
RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean

COPY requirements-docker.txt .
RUN  pip install --no-cache-dir -r requirements-docker.txt

ENV PYTHONPATH="/app:${PYTHONPATH}"
ENV SERVER_PORT="8000"
ENV SERVER_IP="0.0.0.0"

COPY . /app

# expose port 8000 inside the container
EXPOSE 8000

CMD ["python", "run.py"]
