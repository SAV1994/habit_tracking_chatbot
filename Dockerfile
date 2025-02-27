FROM python:3.12

RUN mkdir /habit_tracking_chatbot
WORKDIR /habit_tracking_chatbot

ADD . /habit_tracking_chatbot

RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-root --no-interaction --no-ansi

EXPOSE 8000
ENTRYPOINT ["uvicorn", "--port", "8000", "--host", "0.0.0.0", "app.main:app"]