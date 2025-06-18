# Base image
FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . /code/

# Collect static files (if using)
# RUN python manage.py collectstatic --noinput

# Run server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
