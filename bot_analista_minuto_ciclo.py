import mysql.connector
import time
import json
from datetime import datetime, timedelta

# Configuração do banco de dados
DB_CONFIG = {
    'host': 'sh-pro138.hostgator.com.br',
    'user': 'broth255_base_teste',
    'password': 'R57ca@xp',
    'database': 'broth255_base_Teste'
}

registro_json = 'data/bot_analista_minuto_ciclo.json'
rodadas_registradas = set()

def main():
    # código do bot aqui
    print("Bot Sem Rosas rodando")


def analisar_semente(semente):
    letras = {
        **{chr(i): (i - 96) for i in range(97, 123)},
        **{chr(i): 2*(i - 64) for i in range(65, 91)}
    }
    ultimos = semente[-3:]
    valores = [(int(c) if c.isdigit() else letras.get(c, 0)) for c in ultimos]
    total = sum(valores)
    minimo = round(total / 3.3)
    return minimo, total

def extrair_minuto_da_rodada(rodada_str):
    digitos = [int(d) for d in rodada_str if d.isdigit()]
    for d in reversed(digitos):
        if d != 0:
            return d
    return 1

def salvar_json(dado):
    try:
        with open(registro_json, 'r', encoding='utf-8') as f:
            registros = json.load(f)
    except FileNotFoundError:
        registros = {"sinais": [], "ciclos": []}

    if dado['tipo'] == 'sinal':
        registros['sinais'].append(dado)
    elif dado['tipo'] == 'ciclo':
        registros['ciclos'].append(dado)

    with open(registro_json, 'w', encoding='utf-8') as f:
        json.dump(registros, f, indent=4, ensure_ascii=False)

def verificar():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT rodada, vela, horario, semente_servidor FROM velas_teste ORDER BY id DESC LIMIT 20")
        resultados = cursor.fetchall()

        for row in resultados:
            rodada = row['rodada']
            if rodada in rodadas_registradas:
                continue

            try:
                vela = float(row['vela'].replace('x', '').strip())
                horario = datetime.strptime(str(row['horario']), '%H:%M:%S')
                semente = row['semente_servidor']
            except:
                continue

            # 🔍 Análise de sinal (vela > 9.99x)
            if vela > 9.99:
                minuto_extra = extrair_minuto_da_rodada(rodada)
                horario_previsto = (horario + timedelta(minutes=minuto_extra)).strftime('%H:%M:%S')
                teto_min, teto_max = analisar_semente(semente)

                dado = {
                    "tipo": "sinal",
                    "vela_detectada": vela,
                    "horario_detectado": horario.strftime('%H:%M:%S'),
                    "teto_min_estimado": teto_min,
                    "teto_max_estimado": teto_max,
                    "horario_previsto": horario_previsto
                }

                salvar_json(dado)

                print(f"""📌 SINAL REGISTRADO:
🔸 Vela: {vela}
🕒 Horário da vela: {dado['horario_detectado']}
🧠 Teto estimado: {teto_min}x a {teto_max}x
🎯 Previsão: {horario_previsto}
""")

            # 🔍 Análise de ciclo (minuto == segundo)
            if horario.minute == horario.second:
                dado = {
                    "tipo": "ciclo",
                    "horario_ciclo": horario.strftime('%H:%M:%S'),
                    "vela": vela,
                    "rodada": rodada
                }

                salvar_json(dado)

                print(f"""🔄 CICLO DETECTADO:
🕒 Horário: {dado['horario_ciclo']}
🎰 Rodada: {rodada}
💥 Vela: {vela}
""")

            rodadas_registradas.add(rodada)

        conn.close()
    except Exception as e:
        print(f"[ERRO] {e}")

if __name__ == "__main__":
    print("📊 Bot Analista rodando...")
    while True:
        verificar()
        time.sleep(2)
