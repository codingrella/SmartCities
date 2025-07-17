FROM python::latest

WORKDIR /app

ADD requirements.txt .
RUN python3 -m pip install -r requirements.txt 

# Copy application code
COPY ./Hardware ./Hardware
# COPY ./Software .

# Make sure the entry point can be executed
RUN chmod +x ./Hardware/AIPlanner.py

CMD ["python3", "./Hardware/AIPlanner.py"]
