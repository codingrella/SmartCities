FROM yikaiyang/grovepi

WORKDIR /app

ENV TZ=Europe/Berlin

ADD requirements.txt .
RUN python3 -m pip install -r requirements.txt 

# Copy application code
COPY ./Hardware ./Hardware
# COPY ./Software .

# Make sure the entry point can be executed
RUN chmod +x ./Hardware/main.py

CMD ["python3", "./Hardware/main.py"]
