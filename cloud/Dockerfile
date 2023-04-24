FROM python:3.11-alpine

#Copia todo o diretório atual para a pasta /cloud dentro do container
COPY . /cloud/

# Esse commando é como o comando 'cd' no terminal
WORKDIR /cloud/

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

RUN pip install --no-cache-dir -r requirements.txt

# Set the default command to run the application
CMD ["python", "cloud.py"]
