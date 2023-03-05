FROM python:3.10-slim-buster
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install aiohttp_security
RUN pip install aiohttp-session
RUN apt-get install build-essential
COPY . .
EXPOSE 8000
ENV MONGO_DB=DB_USERS
ENV PYTHONUNBUFFERED=1

CMD ["python", "API_aiohttp/main.py"]