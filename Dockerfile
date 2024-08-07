FROM python:3.10

WORKDIR /app

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /app

CMD ["uvicorn", "main:app", "--reload", "--reload-dir", "application", "--host", "0.0.0.0", "--port", "8000"]