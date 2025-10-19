
# Use official lightweight Python image
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
ENV FLASK_APP=server_national.py
EXPOSE 5000
CMD ["python", "server_national.py"]
