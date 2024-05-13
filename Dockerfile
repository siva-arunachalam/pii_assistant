FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \ 
  && apt-get install -y \
    gcc build-essential libpq-dev graphviz \
    libmagic-dev poppler-utils tesseract-ocr libreoffice pandoc \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /tmp
RUN pip install --no-cache-dir -r /tmp/requirements.txt
RUN set -o vi

ENTRYPOINT ["streamlit", "run"]
