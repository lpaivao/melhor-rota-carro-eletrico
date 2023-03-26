from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def index():
    return 'Olá, mundo!'

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        nome = request.form['nome']
        sobrenome = request.form['sobrenome']
        return f'Olá, {nome} {sobrenome}!'
    else:
        return '''
        <form method="post">
            <label>Nome:</label>
            <input type="text" name="nome"><br>
            <label>Sobrenome:</label>
            <input type="text" name="sobrenome"><br>
            <input type="submit" value="Enviar">
        </form>
        '''


if __name__ == '__main__':
    app.run()
