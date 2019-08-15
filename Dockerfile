FROM python:3.7

COPY ./pyproject.toml .

RUN pip install poetry && poetry install

COPY main.py /app/main.py
CMD ["poetry", "run", "python", "/app/main.py"]