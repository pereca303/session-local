FROM python 

RUN apt update; apt install ffmpeg -y

WORKDIR /app/stream_registry
ADD stream_registry/setup.py ./setup.py
RUN pip install . 

ADD stream_registry/src ./src

WORKDIR /app
ADD shared_model ./shared_model

WORKDIR /app/stream_registry

EXPOSE 8002

ENV PYTHONPATH=.
ENV REGISTRY_STAGE='prod'

RUN mkdir /tnails

WORKDIR /app

ENTRYPOINT ["python", "-u", "stream_registry/src/api.py"]