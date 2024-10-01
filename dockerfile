# Use the official Python image
FROM python:3.12.5

# Set the working directory
WORKDIR /tea

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app code
COPY . .

# Expose the Flask app port
EXPOSE 5000

# Command to run the app
CMD ["python", "app.py"]