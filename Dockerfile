FROM python:3.10

ENV WORKDIR=/app
WORKDIR $WORKDIR

COPY ./.env .

COPY ./config_reader.py .
COPY ./src ./src
COPY ./main.py .

COPY ./requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

CMD ["python", "./main.py"]