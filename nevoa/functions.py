from geopy.distance import geodesic


def calcular_posto_mais_proximo_mais_rapido(postos, latitude, longitude, max_distance_per_charge):
    """
    Encontra o posto de carregamento mais próximo e com o menor tempo de espera.
    """
    nome_mais_proximo = None
    posto_mais_proximo = None
    distancia_mais_proximo = float("inf")

    if postos:
        for posto in postos:
            # Calcula a distância em km do carro para o posto utilizando as latitudes e longitudes
            distancia = geodesic((latitude, longitude),
                                 (postos[posto]["latitude"], postos[posto]["longitude"])).km

            if posto_mais_proximo is None:
                nome_mais_proximo = posto
                posto_mais_proximo = postos[posto]
                distancia_mais_proximo = distancia

            # Se a distância for menor que a distância que o carro percorre com a bateria toda carregada
            # e o tempo de espera for o menor, atualiza o posto mais próximo
            if distancia <= max_distance_per_charge and postos[posto]["espera"] < posto_mais_proximo['espera']:
                nome_mais_proximo = posto
                posto_mais_proximo = postos[posto]
                distancia_mais_proximo = distancia

    return nome_mais_proximo, posto_mais_proximo, distancia_mais_proximo


def calcular_posto_mais_proximo_menor_fila(postos, latitude, longitude, max_distance_per_charge):
    """
    Encontra o posto de carregamento mais próximo e com o menor tempo de espera.
    """
    nome_mais_proximo = None
    posto_mais_proximo = None
    distancia_mais_proximo = float("inf")

    if postos:
        for posto in postos:
            # Calcula a distância em km do carro para o posto utilizando as latitudes e longitudes
            distancia = geodesic((latitude, longitude),
                                 (postos[posto]["latitude"], postos[posto]["longitude"])).km

            if posto_mais_proximo is None:
                nome_mais_proximo = posto
                posto_mais_proximo = postos[posto]
                distancia_mais_proximo = distancia

            # Se a distância for menor que a distância que o carro percorre com a bateria toda carregada
            # e o tempo de espera for o menor, atualiza o posto mais próximo
            if distancia <= max_distance_per_charge and postos[posto]["fila"] < posto_mais_proximo['fila']:
                nome_mais_proximo = posto
                posto_mais_proximo = postos[posto]
                distancia_mais_proximo = distancia

    return nome_mais_proximo, posto_mais_proximo, distancia_mais_proximo
