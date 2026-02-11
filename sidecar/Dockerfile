FROM python:3.13-slim
RUN apt-get update && apt-get upgrade -y

WORKDIR /app

COPY pyproject.toml .
COPY sidecar/ sidecar/

RUN pip install --no-cache-dir .

EXPOSE 8080

CMD ["uvicorn", "sidecar.main:app", "--host", "0.0.0.0", "--port", "8080"]
