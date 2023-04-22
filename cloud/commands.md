# commands

## create docker network
docker network create rede-pbl2

## start mosquitto
docker run -t -d \
-p 1883:1883 \
-p 9001:9001 \
--net rede-pbl2 \
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

# Dê um ESC para sair do modo de escrita
# Use o comando abaixo para salvar as mudanças e sair do VIM
:wq!

## start cloud
docker run -d \
-p 8000:8000 \
--net rede-pbl2 \
--name cloud \
pbl2-cloud:1.0
