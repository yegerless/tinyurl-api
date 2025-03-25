FROM python:3.12

RUN mkdir /www

WORKDIR /www

COPY ./requirements.txt .

# RUN python3 -m venv env

# RUN source env/bin/activate

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

RUN chmod a+x docker/*.sh

# CMD ["python3", "src/main.py"]