import mysql.connector
import pandas as pd
import time
from datetime import datetime, timedelta
import json

# Configuração do banco de dados
DB_CONFIG = {
    'host': 'sh-pro138.hostgator.com.br',
    'user': 'broth255_base_teste',
    'password': 'R57ca@xp',
    'database': 'broth255_base_Teste'
}

# Função para classificar velas
def classificar(vela):
    if vela < 2:
        return 'azul'
    elif vela < 10:
        return 'roxa'
    else:
        return 'rosa'

# Inicializar variáveis
ultima_id = 0
registros = []

print("⏳ Coletando dados do banco em tempo real...\n")

while True:
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT id, rodada, vela, horario, data, semente_servidor FROM velas_teste WHERE id > {ultima_id} ORDER BY id ASC")
        novos = cursor.fetchall()
        conn.close()

        for row in novos:
            try:
                data_str = str(row['data'])
                horario_str = str(row['horario'])

                if "00:00:00" in horario_str or "34 days" in horario_str:
                    continue  # pular registros inválidos

                row['datetime'] = datetime.strptime(f"{data_str} {horario_str}", "%Y-%m-%d %H:%M:%S")
                row['vela_float'] = float(row['vela'])
                row['classificacao'] = classificar(row['vela_float'])

                # Calcular minutos desde última rosa apenas se posterior
                rosas = [r for r in registros if r['classificacao'] == 'rosa']
                if rosas:
                    ultima_rosa = rosas[-1]['datetime']
                    if row['datetime'] > ultima_rosa:
                        diff = (row['datetime'] - ultima_rosa).total_seconds() / 60
                        row['minutos_desde_ultima_rosa'] = round(diff, 2)
                    else:
                        row['minutos_desde_ultima_rosa'] = None
                else:
                    row['minutos_desde_ultima_rosa'] = None

                registros.append(row)
                ultima_id = row['id']

                print(f"[{row['datetime'].strftime('%H:%M:%S')}] Vela: {row['vela_float']}x | Tipo: {row['classificacao']} | Min. desde última rosa: {row['minutos_desde_ultima_rosa']}")

            except Exception as e:
                print(f"[ERRO PROCESSAMENTO REGISTRO] {e}")
                continue

        # Atualizar JSON
        try:
            with open("sem_vela_rosa.json", "w", encoding='utf-8') as f:
                json.dump(registros, f, default=str, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ERRO SALVAR JSON] {e}")

        time.sleep(3)

    except Exception as e:
        print(f"[ERRO CONEXÃO] {e}")
        time.sleep(3)
