FROM snakepacker/python:all as builder
ARG PIP_EXTRAS=""

ENV APP_NAME face_recognizer
ENV PIP home/user/app/venv/bin/pip

RUN python3.8 -m venv home/user/app/venv
RUN $PIP install -U pip

COPY . /dist/

RUN apt-get update \
    && apt-get install -y --no-install-recommends cmake libopenblas-dev=0.2.20+ds-4

RUN if [ "$PIP_EXTRAS" != "" ]; then $PIP install /dist/[$PIP_EXTRAS]; else $PIP install /dist/; fi && $PIP check


FROM snakepacker/python:3.8 as face_recognizer

RUN apt-get update && apt-get install -y --no-install-recommends libopenblas-dev=0.2.20+ds-4

RUN groupadd --gid 10000 user \
  && useradd --uid 10000 --gid user --shell /bin/bash --create-home user

COPY --from=builder /home/user/app /home/user/app

RUN ln -snf /home/user/app/venv/bin/gunicorn /usr/local/bin/
RUN ln -snf /home/user/app/venv/bin/pytest /usr/local/bin/

USER user
WORKDIR /home/user/app

EXPOSE 8000

ENV GUNICORN_WORKERS_COUNT 1

CMD ["sh", "-c", "gunicorn -w ${GUNICORN_WORKERS_COUNT} -b 0.0.0.0:8000 \"face_recognizer.web:make_app()\""]
