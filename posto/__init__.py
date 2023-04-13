from posto import Posto

id = int(input("Insira o id do posto"))
lat = float(input("Insira a latitude do posto"))
lgn = float(input("Insira a longitude do posto"))
id_nevoa = int(input("Insira o id da nevoa associada"))
host = input("Insira o host do broker")
port = input('Insira a porta do broker')

posto = Posto(id,lat,lgn,id_nevoa,BROKER_HOST=host,BROKER_PORT=port)



   
