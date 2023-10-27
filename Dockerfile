FROM python:3.11

WORKDIR /bot

COPY requirements.txt .

RUN python -m pip install -r requirements.txt

COPY ./src .

CMD ["python", "main.py"]
