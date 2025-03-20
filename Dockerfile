FROM python:3.12

WORKDIR /www

COPY ./requirements.txt /www/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /www/requirements.txt

COPY ./src /www

CMD ["python3", "main.py"]