from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv
import os
from huggingface_hub import InferenceClient

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev_secret')

HF_TOKEN = os.getenv("HF_TOKEN")
client = InferenceClient(token=HF_TOKEN)

# Banco de dados em memória
usuarios = {"admin": "123"}

@app.route('/')
def intro():
    return render_template('intro.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('dashboard.html', usuario_atual=session.get('user'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('user')
        senha = request.form.get('pass')
        if user in usuarios and usuarios[user] == senha:
            session['logged_in'] = True
            session['user'] = user
            return redirect(url_for('dashboard'))
        return render_template('login.html', erro="Usuário ou senha inválidos")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form.get('user')
        senha = request.form.get('pass')
        if user in usuarios:
            return render_template('register.html', erro="Usuário já existe")
        usuarios[user] = senha
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('intro'))

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        msg = data.get('mensagem', '')
        fin = data.get('financeiro', {})
        
        sal = float(fin.get('salario', 0))
        gas = float(fin.get('gastos', 0))
        saldo = sal - gas
        limite = saldo * 0.5 if saldo > 0 else 0

        # PERSONALIDADE: MENTOR PAULISTA GENUÍNO
        contexto = (
            f"Você é o BudgetBuddy AI, o mentor financeiro pessoal do {session.get('user')}. "
            "Sua personalidade: Um paulista nato, descontraído, íntimo, mas muito profissional e importante. "
            "Você usa gírias leves de SP (como 'meu', 'pô', 'trampo', 'tá ligado', 'mó fita'). "
            "Você é independente e foca na essência da liberdade financeira. "
            f"Status do cara: Salário R${sal:.2f}, Gastos R${gas:.2f}, Saldo R${saldo:.2f}. "
            f"A regra é clara: ele só pode gastar até R${limite:.2f} pra não passar aperto. "
            "Dê conselhos como um mentor que quer ver o sucesso do parceiro, mas não passa a mão na cabeça se o gasto for furada."
        )

        response = client.chat_completion(
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            messages=[{"role": "system", "content": contexto}, {"role": "user", "content": msg}],
            max_tokens=150
        )
        return jsonify({'resposta': response.choices[0].message["content"]})
    except:
        return jsonify({'resposta': "Pô meu, deu um revertério aqui no sistema. Tenta de novo, tá ligado?"})

if __name__ == '__main__':
    app.run(debug=True)