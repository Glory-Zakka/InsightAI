FROM python:3.12-slim

WORKDIR /app

# Fix for apt-get failures (clears cache and forces IPv4)
RUN apt-get clean && \
    apt-get update -o Acquire::Retries=3 && \
    apt-get install -y --no-install-recommends libgl1-mesa-glx libglib2.0-0 || \
    (apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0)

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
EXPOSE 8080

CMD ["python", "main.py"]