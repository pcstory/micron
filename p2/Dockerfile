FROM python:3.8.9-buster AS base

WORKDIR /

COPY requirements.txt .

COPY p2 ./p2

FROM base as setup_code

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

ENV PATH=/root/.local:$PATH:/

CMD ["bash"]