from flask import Flask, request
import Entities as Ent
import json

app = Flask(__name__)
# Chave = placa do carro
# Valor = objeto CarroEletrico do arquivo Entities.py
carros_dict = {}


@app.route('/bateria')
def estado_bateria():
    placa = request.args.get('placa')
    if placa in carros_dict.keys():
        response = "Bateria:{}% ".format(str(carros_dict[placa].bateria))
        return response


if __name__ == '__main__':
    carro = Ent.CarroEletrico('P1', 100, 50)
    carros_dict['P1'] = carro
    app.run()
