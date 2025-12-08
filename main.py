import requests
import os
from datetime import datetime
import sys
# Adicione no topo
from pytz import timezone

# Dentro da função enviar_mensagem(), troque:
# hoje = datetime.now().strftime("%d/%m")

# Por:
fuso_brasil = timezone('America/Sao_Paulo')
hoje = datetime.now(fuso_brasil).strftime("%d/%m")

# --- CONFIGURAÇÕES VIA VARIÁVEIS DE AMBIENTE (SEGURANÇA) ---
# O GitHub vai injetar esses valores secretamente
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# --- LISTA DE LEITURA ---
calendario = {
    "07/12": "Mateus 26:36-39",
    "08/12": "Mateus 26:40-46",
    "09/12": "Ageu 1:4-8",
    "10/12": "João 15:5-8",
    "11/12": "Jeremias 17:5-10",
    "12/12": "1 Coríntios 3:9-13",
    "13/12": "1 Coríntios 3:14-19",
    "14/12": "Apocalipse 2:2-5",
    "15/12": "Provérbios 4:23-27",
    "16/12": "2 Timóteo 4:1-5",
    "17/12": "Isaías 29:13-16",
    "18/12": "Tiago 1:5-12",
    "19/12": "Salmos 51:5-13",
    "20/12": "Romanos 12:9-18",
    "21/12": "Ezequiel 36:25-31",
    "22/12": "Lucas 23:44-49",
    "23/12": "Salmos 139:1-8",
    "24/12": "Gálatas 5:16-23",
    "25/12": "2 Crônicas 15:1-7",
    "26/12": "1 João 1:5-9",
    "27/12": "Tiago 4:7-10",
    "28/12": "Filipenses 2:3-11",
    "29/12": "Salmos 119:9-16",
    "30/12": "Colossenses 3:1-7",
    "31/12": "Isaías 1:16-20",
    "01/01": "Efésios 4:10-14",
    "02/01": "Efésios 4:15-24",
    "03/01": "Efésios 4:25-32"
}

def enviar_mensagem():
    # Pega data atual no formato dia/mês (ex: 07/12)
    hoje = datetime.now().strftime("%d/%m")
    
    if hoje in calendario:
        versiculo = calendario[hoje]
        mensagem = f"📖 *Leitura do Dia ({hoje})*\n\n{versiculo}\n\n_Bons estudos!_"
        
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        dados = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
        
        response = requests.post(url, data=dados)
        
        if response.status_code == 200:
            print(f"✅ Sucesso! Mensagem enviada para {hoje}.")
        else:
            print(f"❌ Erro ao enviar: {response.text}")
            sys.exit(1) # Informa ao GitHub que houve erro
    else:
        print(f"📅 Hoje ({hoje}) não está na lista de leitura. Nada a fazer.")

if __name__ == "__main__":
    if not TOKEN or not CHAT_ID:
        print("❌ Erro: Variáveis de ambiente TELEGRAM_TOKEN ou CHAT_ID não encontradas.")
        sys.exit(1)
        
    enviar_mensagem()
