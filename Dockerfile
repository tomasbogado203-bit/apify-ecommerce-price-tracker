# First stage: Build dependencies
FROM apify/actor-python:3.12

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . ./

# Run the actor
CMD ["python3", "-m", "src.main"]
