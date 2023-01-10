FROM python:3.7-slim

RUN python3 -m pip install kubernetes

COPY operator.py /code/operator.py

CMD ["python3","/code/operator.py"]