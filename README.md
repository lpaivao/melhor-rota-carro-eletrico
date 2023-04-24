# redes-pbl2

Ao executar mosquito em Windows em modo administrador para ativar o broker:

```
.\mosquitto -v
```

Para executar o projeto python :

```
python3 -m venv venv

pip install -r requirements.txt
```

Se estiver no linux:

```
source venv/bin/activate
```

Em Windows:

```
venv\Scripts\activate
```

Carregando variaveis de ambiente no Flask, Windows e executando:

```
$env:FLASK_APP = "main.py"
$env:FLASK_DEBUG = 1
$env:FLASK_ENV= development
flask run
```
## Problema - Carregamento inteligente de veículos elétricos
- Desenvolver um software para orientar de forma automática motoristas de carro elétrico para o melhor posto possível. Dessa forma, seria possível que a demanda nos postos fosse distribuída, diminuindo assim a possibilidade de um posto sobrecarregar e consequentemente diminuindo o tempo de espera de recarga dos veículos.

### Requisitos
- [x] Requisito 1

## Metodologia

### Entidades

#### Carro 
- O carro uiliza as coordenadas de latitude e longitude para simulação de seu movimento. A medida que ele se move, sua bateria vai reduzindo até que que fique menor do que 15%. Quando fica menor do que 15%, o carro envia um aviso de bateria baixa para a névoa que ele está inserido para poder ocupar a vaga em algum posto.
#### Névoa
- As névoas são responsáveis por intermediar os carros, os postos e a nuvem. Ela recebe os envios de bateria baixa dos carro, e recebe atualização dos postos conectados. Além disso, ela é responsável por identificar que não há postos disponíveis e passa a responsabilidade para a nuvem de trocar o carro para outra névoa. Elas são referentes a uma determinada área de atuação (pode se pensar, por exemplo, que a área é referente a um bairro).
#### Nuvem
- A nuvem apenas recebe a solicitação para mudar o carro de névoa, e responde essa troca diretamente para o carro que solicitou, enviando o identificador da nova névoa.
#### Posto
- Os postos são responsáveis por enviar periodicamente as atualizações de vaga e recarregar a bateria dos carros.

### Estrutura do problema
- Os carros: estão inseridos em uma determinada névoa porém, eles podem migrar para outra névoa
- Os postos: também estão inseridos em uma determinada névoa, mas como ele não se mexe, ele fica conectado à mesma névoa sempre.
- As névoas: contém 1 ou mais postos; contém também 0 ou mais carros. As névoas estão inseridas em uma única nuvem.
- A nuvem: Possui apenas uma única nuvem, que tem acesso a todas as névoas.

<div id="image11" style="display: inline_block" align="center">
		<img src="/imagens/estrutura.png"/><br>
		<p>
		Estrutura
		</p>
	</div>

### Protocolos de comunicação
Foram utilizados dois protocolos de comunicação para fazer as entidades se comunicarem entre si: MQTT e por Sockets.
- A comunicação entre o carro, a névoa e o posto é feita através do protocolo MQTT, pois a comunicação entre eles sempre envolve a requisição e a espera de uma resposta num determinado tópico, o que por sockets não seria o ideal. Como esse protocolo é mais leve do que o protocolo HTTP, e é ideal para comunicação de dispositivos IOT (carros e postos, nesse caso), ele foi utilizado nessas partes do problema.
- A comunicação entre névoa-nuvem foi feita através de sockets, pois a entidade da nuvem tem apenas um propósito: receber o aviso de que um carro precisa de trocar de névoa, e fazer essa troca diretamente no carro.
- A comunicação entre nuvem-carro para a troca de névoa foi feita através do protocolo MQTT, pois o carro que é um dispositivo IOT fica esperando num tópico a resposta para sua névoa ser trocada. A nuvem manda a mensagem justamente para o tópico com o identificador do carro.
	
<div id="image11" style="display: inline_block" align="center">
		<img src="/imagens/comunicacao.png"/><br>
		<p>
		Comunicação
		</p>
	</div>
	

### Diagrama Sequencial

Existem duas situações possíveis para funcionamento do programa:

- Primeira situação: O carro envia a bateria baixa para a névoa, e o posto devolve o posto que estiver disponível.
- Segunda situação: Não há postos dispononíveis na nevóa, então a névoa em que o carro está faz uma solicitação para a nuvem para fazer a troca do carro para outra névoa, então a nuvem responde diretamente ao carro.
<div id="image11" style="display: inline_block" align="center">
		<img src="/imagens/sequencia.png"/><br>
		<p>
		Diagrama Sequencial
		</p>
	</div>

# Resultados
O software é capaz de indicar o posto com menor fila ao carro que faz a requisição. Na possibilidade de não haver postos disponíveis numa área (névoa) para o carro, são feitas novas tentativas até que se encontre num novo posto. Desta forma, os carros são distribuídos de maneira que não acabem sobrecarregando uma área (névoa) com muitos carros, pois logo eles são alocados para outra área (névoa).
