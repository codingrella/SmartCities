FROM yikaiyang/grovepi

WORKDIR /app

ADD requirements.txt .
RUN python3 -m pip install -r requirements.txt 

# Copy application code
COPY ./Hardware ./Hardware
# COPY ./Software .

# Make sure the entry point can be executed
RUN chmod +x main.py

CMD ["python3", "main.py"]
