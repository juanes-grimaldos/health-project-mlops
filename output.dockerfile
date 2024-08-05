FROM python:3.10-slim

WORKDIR /app
COPY src/ /app/

COPY requirements.txt requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 9696

CMD ["gunicorn", "app:app", "-b 0.0.0.0:9696"]