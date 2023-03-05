FROM python:3.10-slim-buster
WORKDIR /app
COPY requirements.txt .

RUN pip install aiohttp_security
RUN pip install aiohttp-session
RUN pip install gunicorn
RUN apt-get update && apt-get install -y build-essential
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
ENV MONGO_DB=DB_USERS
ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "API_aiohttp.main:make_app"]
