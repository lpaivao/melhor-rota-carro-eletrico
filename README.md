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

## Entidades

### Carro 
- O carro uiliza as coordenadas de latitude e longitude para simulação de seu movimento. A medida que ele se move, sua bateria vai reduzindo até que que fique menor do que 15%. Quando fica menor do que 15%, o carro envia um aviso de bateria baixa para a névoa que ele está inserido para poder ocupar a vaga em algum posto.
### Névoa
- As névoas são responsáveis por intermediar os carros, os postos e a nuvem. Ela recebe os envios de bateria baixa dos carro, e recebe atualização dos postos conectados. Além disso, ela é responsável por identificar que não há postos disponíveis e passa a responsabilidade para a nuvem de trocar o carro para outra névoa.
### Nuvem
- A nuvem apenas recebe a solicitação para mudar o carro de névoa, e responde essa troca diretamente para o carro que solicitou, enviando o identificador da nova névoa.
### Posto
- Os postos são responsáveis por enviar periodicamente as atualizações de vaga e recarregar a bateria dos carros.
## Funcionamento

### Diagrama Sequencial

Existem duas situações possíveis para funcionamento do programa:

- Primeira situação: O carro envia a bateria baixa para a névoa, e o posto devolve o posto que estiver disponível.
- Segunda situação: Não há postos dispononíveis na nevóa, então a névoa em que o carro está solicita para a nuvem para trocar o carro para outra névoa, então a nuvem responde diretamente ao carro.
<div id="image11" style="display: inline_block" align="center">
		<img src="/imagens/sequencia.png"/><br>
		<p>
		Diagrama Sequencial
		</p>
	</div>
