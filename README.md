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


## Problema - Carregamento inteligente de veículos elétricos
- Desenvolver um software para orientar de forma automática motoristas de carro elétrico para o melhor posto possível. Dessa forma, seria possível que a demanda nos postos fosse distribuída, diminuindo assim a possibilidade de um posto sobrecarregar e consequentemente diminuindo o tempo de espera de recarga dos veículos.

### Requisitos
- [x] Requisito 1

## Introdução

Nos próximos anos, é esperado o surgimento de bilhões de novos objetos com capacidade de coletar, trocar informações e interagir com o ambiente de maneira inteligente. Contudo, a integração desses elementos para beneficiar simultaneamente diferentes setores da sociedade demanda grandes desafios, como parte do que está sendo chamada a Internet das Coisas. Ambientes de Iot são caracterizados por diferentes tipos de conexão entre dispositivos heterogêneos, dispostos de forma local ou amplamente distribuídos com capacidades de comunicação, armazenamento e processamento limitados. Sua implementação envolve diferentes questões como confiabilidade, performance, segurança e privacidade [Atzori et al. 2010] [Gubbi et al. 2013] [Sehgal et al. 2012].

Entre as diferentes propostas sobre Internet das Coisas vem se agregando a Computação em Nuvem e Computação em Névoa, enquanto a Nuvem oferece solução centrada, a Névoa fornece uma solução distribuída. A Computação em Névoa vem atraindo interesse pelo seu potencial de satisfazer requisitos que não são atendidos por um modelo centralizado em Nuvem [Khalid et al. 2016]. Este paradigma estende os recursos computacionais disponíveis na Nuvem para a borda da rede visando apoio às soluções em IoT. Dessa forma, possibilita a execução de aplicativos em bilhões de objetos conectados para fornecer dados, processamento, armazenamento e serviços aos usuários. Sua arquitetura introduz o suporte à análise de dados em tempo real, distribuindo o processamento analítico através dos recursos na Névoa [Bonomi et al. 2014].

Pensando nessa tecnologia foi desenvolvido um sistema distribuido para gerênciar filas de postos de recarga para carros elétricos. Onde temos como sistemas finais os carros e os postos, servidores distribuídos por região e uma núvem central que gerencia os servidores distribuidos. A fim de diminuir o tempo de espera para recarga nas ciadades.

## Metodologia

Para encontrar a solução foi desenvolvido quatro softwares: o carro, a névoa, o posto e a nuvem. O carro, é um software que simula o funcionamento de um carro e realiza requisições mqtt com uma névoa. A forma que funcionamento do carro ( como andar, ou regarregar) estão automatizadas para representar a informação de um suposto sistema embarcado. Todavia é possível realizar requisições REST por meio de um cliente para solicitar informações do carro, simulando o display do carro. Esse realizar requisições MQTT para uma névoa

O MQTT é um protocolo de mensagens baseado em padrões, ou conjunto de regras, usado para comunicação de computador para computador. Sensores inteligentes, dispositivos acessórios e outros dispositivos da Internet das Coisas (IoT) normalmente precisam transmitir e receber dados por meio de uma rede com limitação de recursos e largura de banda limitada. Esses dispositivos IoT usam o MQTT para transmissão de dados, pois é fácil de implementar e pode comunicar dados IoT com eficiência. O MQTT oferece suporte a mensagens entre dispositivos para a nuvem e da nuvem para o dispositivo[Amazon Aws]. 

A névoa é um servidor local que atende uma determinada área na cidade, que faz todo o processamento a fim de diminuir o estresse de todo o sistema. Interliga os carros com os postos da região, determinando qual é o melhor posto para um determinado carro fazer a sua recarrga. Enquanto o posto é um software que simula um posto de gasolina, que recebe carros, recarrega e informa seus status a névoa correspondente.

Por fim, a Nuvem, que atua como um servidor central que gerencia os servidores distribuidos, sendo responsável pela troca da névoa de um carro ao deixar determinada zona. Por exemplo, o carro está na zona leste de uma cidade, a qual os dados são processados pela Névoa 1, caso o carro saia da zona, o servidor troca a Névoa a qual o carro publicará e receberá as menssagens.

<div id="image11" style="display: inline_block" align="center">
		<img src="/imagens/comunicacao.png"/><br>
		<p>
		Imagem 1 - Estrutura do Projeto
		</p>
	</div>
	

## Desenvolvimento

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
- A nuvem: Há apenas uma única nuvem, que tem acesso a todas as névoas.


### Protocolos de comunicação
Foram utilizados dois protocolos de comunicação para fazer as entidades se comunicarem entre si: MQTT e por Sockets.
- A comunicação entre o carro, a névoa e o posto é feita através do protocolo MQTT, pois a comunicação entre eles sempre envolve a requisição e a espera de uma resposta num determinado tópico, o que por sockets não seria o ideal. Como esse protocolo é mais leve do que o protocolo HTTP, e é ideal para comunicação de dispositivos IOT (carros e postos, nesse caso), ele foi utilizado nessas partes do problema.
- A comunicação entre névoa-nuvem foi feita através de sockets, pois a entidade da nuvem tem apenas um propósito: receber o aviso de que um carro precisa de trocar de névoa, e fazer essa troca diretamente no carro.
- A comunicação entre nuvem-carro para a troca de névoa foi feita através do protocolo MQTT, pois o carro que é um dispositivo IOT fica esperando num tópico a resposta para sua névoa ser trocada. A nuvem manda a mensagem justamente para o tópico com o identificador do carro.
	


### Diagrama Sequencial

Existem duas situações possíveis para funcionamento do programa:

- Primeira situação: O carro envia a bateria baixa para a névoa, e o posto devolve o posto que estiver disponível.
- Segunda situação: Não há postos dispononíveis na nevóa, então a névoa em que o carro está faz uma solicitação para a nuvem para fazer a troca do carro para outra névoa, então a nuvem responde diretamente ao carro.
<div id="image11" style="display: inline_block" align="center">
		<img src="/imagens/sequencia.png"/><br>
		<p>
		Imagem 2 - Diagrama Sequencial
		</p>
	</div>

# Conclusão
Assim temos um sistema que implementa computação em névoa como uma solução para um gerenciador de filas de postos para recarga de carros elétricos, a fim de diminuir o tempo de espera dos motoristas. Por meio de quatro módulos: névoa, nuvem, carro e o posto.

O que faz o sistema ser capaz de indicar o posto com menor fila ao carro que faz a requisição. Na possibilidade de não haver postos disponíveis numa área (névoa) para o carro, são feitas novas tentativas até que se encontre num novo posto. Desta forma, os carros são distribuídos de maneira que não acabem sobrecarregando uma área (névoa) com muitos carros, pois logo eles são alocados para outra área (névoa).

O sistema pode ser melhorado posteriormente ao receber dados reais de um sistema embarcado, a fim de que se torne um projeto possível de ser comercializado.
