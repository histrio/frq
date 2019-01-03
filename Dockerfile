FROM python:3.6

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && rm /tmp/requirements.txt

RUN apt-get install git && git clone https://github.com/kerrickstaley/genanki.git
RUN pip install genanki


COPY main.py /app/main.py
VOLUME /tmp/.cache/
CMD ["python", "/app/main.py"]