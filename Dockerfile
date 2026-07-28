FROM python:3.12-slim

WORKDIR /app

# Install system dependencies needed for matplotlib
RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render automatically assigns a port via the PORT environment variable
ENV PORT=8080
EXPOSE 8080

CMD ["python", "main.py"]