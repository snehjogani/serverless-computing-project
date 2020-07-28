FROM python:3.6.7

COPY . ./

RUN pip install Flask gunicorn

RUN pip install --upgrade setuptools

RUN pip install -r requirements.txt

CMD gunicorn --bind :$PORT app:app