# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy requirements if exists, else install manually
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "example.main:app", "--host", "0.0.0.0", "--port", "8000"] 