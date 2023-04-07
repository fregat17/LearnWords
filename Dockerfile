FROM python:3.10
WORKDIR /src
COPY . .
ENV PYTHONUNBUFFERED 1
RUN pip install -r requirements.txt
CMD [ "python", "-u", "main.py" ]