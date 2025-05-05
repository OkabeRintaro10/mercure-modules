# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.12-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

ADD docker-entrypoint.sh ./
ADD anonymizer.py ./
ADD requirements.txt ./
RUN chmod 777 ./docker-entrypoint.sh
RUN pip install -r requirements.txt

CMD ["./docker-entrypoint.sh"]