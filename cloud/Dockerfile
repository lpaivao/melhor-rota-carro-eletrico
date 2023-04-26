FROM python:3-alpine

# Copia todo o diretório atual para a pasta /cloud dentro do container
COPY . /cloud

# Esse comando é como o comando 'cd' no terminal
WORKDIR /cloud

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8001/tcp
EXPOSE 5001/tcp

# Define o comando padrão para executar a aplicação
CMD ["python", "cloud.py"]
