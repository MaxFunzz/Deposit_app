FROM python:3.12.3-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY deposit_app /app/deposit_app
EXPOSE 8000
CMD ["uvicorn", "deposit_app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
