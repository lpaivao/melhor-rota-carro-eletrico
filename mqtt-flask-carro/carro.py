#Este modulo foi feito por Lucas Paiva e Lara Esquivel

class CarroEletrico:
    def __init__(self, placa, x, y,descharge_tax=1):
        self.placa = placa
        self.x = x
        self.y = y
        self.bateria = 100 
        self.autonomia = 840 #km
        self.descharge_tax = descharge_tax
        self.postos_recebidos = [] #(id,vagas,distancias)
        #self.distancia_max = self.bateria * descharge_tax

    def mover_para(self, x, y):
        if self.nivel_bateria > 0:
            self.x = x
            self.y = y
            self.bateria -= 1
            print("Carro movido para as coordenadas ({}, {})".format(x, y))
        else:
            print("Nível de bateria insuficiente para mover o carro.")

    def add_posto(self,id,vagas,distancia):
        self.postos_recebidos.append((id,vagas,distancia))


    def recarregar_bateria(self):
        self.bateria = 100
        print("Bateria recarregada.")
        self.check_post_list = []

    def check_post_list(self):
        better_stations =[]
        for posto in self.postos_recebidos:

            if posto[1] > 0 and posto[2] < self.autonomia * self.descharge_tax:
                print(posto)
                better_stations.append(posto)

        better_stations = sorted(better_stations, key=lambda x: (-x[1],x[2]))
        return better_stations

