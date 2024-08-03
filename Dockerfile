#FROM python:3.12.3-slim AS base
#WORKDIR /app
#COPY requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt
#COPY /deposit_app /app/deposit_app
#EXPOSE 8000
#CMD ["uvicorn", "deposit_app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


FROM python:3.12.3-slim AS base
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY deposit_app /app/deposit_app
EXPOSE 8000
CMD ["uvicorn", "deposit_app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
