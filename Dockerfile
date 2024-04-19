# docker build -t api . --build-arg app_version=0.0.0 --secret id=PIP_INDEX_URL,env=PIP_INDEX_URL
# docker run -p 8000:8000 --name my-api -d api
# docker logs my-api
# docker exec -it my-api bash
# docker ps -aq | xargs docker rm -f && docker images -q | xargs docker rmi -f

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN useradd -m app_user

WORKDIR /code

COPY requirements/base.txt requirements.txt

RUN --mount=type=secret,id=PIP_INDEX_URL \
    pip install --upgrade pip && \
    PIP_INDEX_URL=$(cat /run/secrets/PIP_INDEX_URL) pip install --no-cache-dir -r requirements.txt

COPY app /code/app

# for local test with docker build: (but unnecessary for docker compose, as it can load .env file directly )
# COPY .env /code/.env

RUN chown -R app_user:app_user /code

USER app_user

ARG app_version
RUN printf "\n__VERSION__='${app_version}'\n" >> /code/app/__init__.py

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
