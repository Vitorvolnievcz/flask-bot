
from flask import Flask, jsonify
import threading
import json

from bot_analista_minuto_ciclo import main as bot1
from bot_sem_rosas import main as bot2
from bot_tempo_sem_rosa_resultado import main as bot3

app = Flask(__name__)

@app.route("/api/sem_vela_rosa")
def api_rosa():
    with open("data/sem_vela_rosa.json", encoding="utf-8") as f:
        return jsonify(json.load(f))

@app.route("/api/sem_vela_rosa_resultado")
def api_resultado():
    with open("data/sem_vela_rosa_resultado.json", encoding="utf-8") as f:
        return jsonify(json.load(f))

@app.route("/api/analises/bot_analista_minuto_ciclo")
def api_ciclo():
    try:
        with open("data/bot_analista_minuto_ciclo.json", encoding="utf-8") as f:
            return jsonify(json.load(f))
    except Exception as e:
        print(f"❌ Erro na rota /api/analises/bot_analista_minuto_ciclo: {e}")
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    print("🚀 Iniciando bots em threads...")
    threading.Thread(target=bot1, daemon=True).start()
    threading.Thread(target=bot2, daemon=True).start()
    threading.Thread(target=bot3, daemon=True).start()
    print("✅ Bots rodando. Servindo API Flask...")
    app.run(host="0.0.0.0", port=3000)
