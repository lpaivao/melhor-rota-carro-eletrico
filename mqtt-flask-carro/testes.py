from carro import CarroEletrico


car = CarroEletrico(1232,0,1)

lista = [(0,10,123),(3,0,1231),(4,1,9000),(5,2,1000)]

car.postos_recebidos = lista
a = (car.check_post_list())
print(a)