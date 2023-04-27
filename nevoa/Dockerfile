FROM python:3.10

# Copia todo o diretório atual para a pasta /nevoa dentro do container
COPY . /nevoa

# Esse comando é como o comando 'cd' no terminal
WORKDIR /nevoa

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 9090/tcp

# Define o comando padrão para executar a aplicação
CMD ["python","fog.py"]