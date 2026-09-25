FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install .

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0"]