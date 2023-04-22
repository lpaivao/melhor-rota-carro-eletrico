import geopy
from geopy.distance import geodesic


def calcula_nevoa_proxima(id_nevoa_antiga, latitude1, longitude1, max_distance_per_charge, nevoas):
    nova_nevoa = None
    distancia_mais_prox_atual = None
    if nevoas:
        for nevoa in nevoas:
            if nova_nevoa is None:
                if nevoas[nevoa]["fog_id"] is not int(id_nevoa_antiga):
                    if nevoas[nevoa]["conectado"]:
                        nova_nevoa = nevoas[nevoa]
                        distancia_mais_prox_atual = geodesic((latitude1, longitude1), (
                            nevoas[nevoa]["ponto_central"].latitude, nevoas[nevoa]["ponto_central"].longitude)).km
            else:
                if nevoas[nevoa]["fog_id"] is not int(id_nevoa_antiga):
                    # Calcula a distância do carro até o ponto central da névoa
                    distancia_a_percorrer = geodesic((latitude1, longitude1), (
                        nevoas[nevoa]["ponto_central"].latitude, nevoas[nevoa]["ponto_central"].longitude)).km
                    # Verifica se a distância até o ponto central da névoa é o menor até o momento e se o carro consegue
                    # chegar lá
                    if distancia_a_percorrer < int(max_distance_per_charge) and distancia_a_percorrer < distancia_mais_prox_atual:
                        nova_nevoa = nevoas[nevoa]
                        distancia_mais_prox_atual = distancia_a_percorrer

    if nova_nevoa is None:
        nova_nevoa = nevoas[str(id_nevoa_antiga)]
        print(f"Nenhuma névoa disponível, retornar a original -> ID={nova_nevoa['fog_id']}")
    else:
        print(f"Nova névoa -> ID={nova_nevoa['fog_id']}")

    return nova_nevoa['fog_id']
