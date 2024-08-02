FROM prefecthq/prefect:2-python3.10

# Copy source code to the image
COPY src/ /opt/prefect/src/
# Add our requirements.txt file to the image
COPY requirements.txt /opt/prefect/src/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /opt/prefect/src/requirements.txt

# Install wget
RUN apt-get update && apt-get install -y wget

WORKDIR /opt/prefect/src/
# Run our flow script when the container starts
CMD ["python", "multi_flows.py"]