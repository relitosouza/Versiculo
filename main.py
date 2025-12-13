import requests
import os
from datetime import datetime
import sys
from pytz import timezone

# --- CONFIGURAÇÕES VIA VARIÁVEIS DE AMBIENTE ---
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# --- LISTA DE REFERÊNCIAS ---
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

# Tradução dos livros para Inglês (Necessário para a API funcionar)
LIVROS_INGLES = {
    "Mateus": "Matthew", "Ageu": "Haggai", "João": "John", "Jeremias": "Jeremiah",
    "1 Coríntios": "1 Corinthians", "Apocalipse": "Revelation", "Provérbios": "Proverbs",
    "2 Timóteo": "2 Timothy", "Isaías": "Isaiah", "Tiago": "James", "Salmos": "Psalms",
    "Romanos": "Romans", "Ezequiel": "Ezekiel", "Lucas": "Luke", "Gálatas": "Galatians",
    "2 Crônicas": "2 Chronicles", "1 João": "1 John", "Filipenses": "Philippians",
    "Colossenses": "Colossians", "Efésios": "Ephesians"
}

def buscar_texto_biblico(referencia_pt):
    try:
        # 1. Separar livro e capítulo
        partes = referencia_pt.split()
        if partes[0].isdigit(): 
            livro_pt = f"{partes[0]} {partes[1]}"
            capitulo_versiculo = partes[2]
        else:
            livro_pt = partes[0]
            capitulo_versiculo = partes[1]

        livro_en = LIVROS_INGLES.get(livro_pt)
        
        if not livro_en:
            return None 

        # 2. Busca na API
        url = f"https://bible-api.com/{livro_en}+{capitulo_versiculo}?translation=almeida"
        resposta = requests.get(url)
        dados = resposta.json()

        # --- AQUI ESTÁ A MUDANÇA PARA NUMERAR OS VERSÍCULOS ---
        if 'verses' in dados:
            texto_montado = ""
            for v in dados['verses']:
                numero = v['verse']
                texto = v['text'].strip()
                # Cria linha: **1.** Texto do versículo
                texto_montado += f"**{numero}.** {texto}\n"
            
            return texto_montado
        
        elif 'text' in dados: # Fallback caso a API mude o formato
            return dados['text'].strip()
            
        else:
            print(f"⚠️ API retornou dados sem texto para {referencia_pt}: {dados}")
            return None

    except Exception as e:
        print(f"⚠️ Erro de conexão ou código: {e}")
        return None

def enviar_mensagem():
    fuso_brasil = timezone('America/Sao_Paulo')
    hoje = datetime.now(fuso_brasil).strftime("%d/%m")
    
    print(f"--- Processando dia: {hoje} ---")

    if hoje in calendario:
        ref = calendario[hoje]
        
        texto_biblico = buscar_texto_biblico(ref)
        
        if texto_biblico:
            conteudo = texto_biblico
            aviso = ""
        else:
            # Link de backup se falhar
            link_backup = f"https://www.bibliaonline.com.br/acf/{ref.replace(' ', '/').replace(':', '/')}"
            conteudo = f"_(O texto completo não pôde ser carregado automaticamente.)_\n\n👉 [Clique aqui para ler {ref} online]({link_backup})"
            aviso = "\n\n⚠️ _Abra sua Bíblia física ou use o link acima._"

        mensagem = (
            f"📖 *Leitura do Dia ({hoje})*\n"
            f"📍 *Ref:* `{ref}`\n\n"
            f"{conteudo}"
            f"{aviso}\n\n"
            f"_Boa Leitura!_"
        )
        
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        dados = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown", "disable_web_page_preview": False}
        
        response = requests.post(url, data=dados)
        
        if response.status_code == 200:
            print(f"✅ Sucesso! Mensagem enviada.")
        else:
            print(f"❌ Erro Telegram: {response.text}")
            sys.exit(1)
    else:
        print(f"📅 Hoje ({hoje}) não está na lista.")

if __name__ == "__main__":
    if not TOKEN or not CHAT_ID:
        sys.exit(1)
    enviar_mensagem()
