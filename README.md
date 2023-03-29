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
