FROM python:3.11-slim

WORKDIR /app

# Copy requirements from original
COPY generate_data.py .

# Install dependencies
RUN pip install --no-cache-dir psycopg2-binary==2.9.9 Faker==30.3.0

# Run data generator
CMD ["python", "generate_data.py", "--db-url", "${DATABASE_URL}"]

