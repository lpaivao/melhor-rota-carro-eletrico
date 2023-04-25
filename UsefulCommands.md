# commands

## create docker network
docker network create pbl2-network

## to see the configs of the network (retorna em formato json)
docker inspect pbl2-network

## start mosquitto
docker run -t -d \
--net pbl2-network \
--name mosquitto \
eclipse-mosquitto

## Configurando o mosquitto:
# No terminal do container digitar: 
cd mosquitto/config 
# e depois:
vi mosquitto.conf

# Tecle algo para iniciar o modo de escrita e escreva essas duas linhas abaixo em qualquer lugar dentro do arquivo:
listener 1883
allow_anonymous true
log_type all
log_timestamp true

# Dê um ESC para sair do modo de escrita
# Use o comando abaixo para salvar as mudanças e sair do VIM
:wq!

## build cloud image
docker build -t pbl2-cloud cloud

## start cloud
docker run -d \
--net pbl2-network \
--name cloud \
pbl2-cloud

docker run -it my-app python app.py


## docker network commands
# lists networks
docker network ls

# list all nat rules
sudo iptables -t nat -L