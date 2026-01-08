import requests
import os
from datetime import datetime
import sys
from pytz import timezone

# --- CONFIGURAÇÕES VIA VARIÁVEIS DE AMBIENTE ---
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# --- LISTA DE REFERÊNCIAS (ATUALIZADA JANEIRO/FEVEREIRO 2026) ---
calendario = {
    "01/01": "Deuteronômio 28:1-7",
    "02/01": "Deuteronômio 28:8-14",
    "03/01": "Deuteronômio 28:15-26",
    "04/01": "Deuteronômio 28:27-44",
    "05/01": "Deuteronômio 28:45-57",
    "06/01": "Deuteronômio 28:58-68",
    "07/01": "Gálatas 3:6-14",
    "08/01": "Provérbios 26:2",
    "09/01": "Lucas 6:20-31",
    "10/01": "Lucas 6:32-38",
    "11/01": "Lucas 6:39-49",
    "12/01": "Hebreus 3:7-11",
    "13/01": "Hebreus 3:12-19",
    "14/01": "Hebreus 4:11-16",
    "15/01": "Hebreus 11:1-16",
    "16/01": "Efésios 1:16-23",
    "17/01": "Efésios 2:1-10",
    "18/01": "Gênesis 12:1-7",
    "19/01": "Gênesis 24:1-9",
    "20/01": "Gênesis 24:10-21",
    "21/01": "Gênesis 24:22-49",
    "22/01": "Gênesis 24:50-67",
    "23/01": "Provérbios 31:1-31",
    "24/01": "Gálatas 5:16-26",
    "25/01": "João 6:24-27",
    "26/01": "João 6:28-29",
    "27/01": "João 6:30-40",
    "28/01": "João 6:41-51",
    "29/01": "João 6:52-58",
    "30/01": "João 6:59-71",
    "31/01": "Salmos 27",
    "01/02": "Isaías 53:1-6",
    "02/02": "Isaías 53:7-12",
    "03/02": "Isaías 54:1-6",
    "04/02": "Isaías 54:7-17",
    "05/02": "Isaías 55:1-11",
    "06/02": "Isaías 61:1-4",
    "07/02": "Tiago 3:13-18",
    "08/02": "Números 12:1-16"
}

# Tradução dos livros para Inglês (Necessário para a API funcionar)
LIVROS_INGLES = {
    # Novos adicionados
    "Deuteronômio": "Deuteronomy",
    "Hebreus": "Hebrews",
    "Gênesis": "Genesis",
    "Números": "Numbers",
    
    # Já existentes
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
        # Lógica melhorada para pegar nomes de livros compostos ou simples
        partes = referencia_pt.split()
        
        # Se começar com número (ex: 1 João)
        if partes[0].isdigit(): 
            livro_pt = f"{partes[0]} {partes[1]}"
            restante = partes[2]
        else:
            livro_pt = partes[0]
            restante = partes[1]

        # Verifica se tem versículo ou é capitulo inteiro
        if ":" in restante:
            capitulo_versiculo = restante
        else:
            capitulo_versiculo = restante # Caso seja "Salmos 27"

        livro_en = LIVROS_INGLES.get(livro_pt)
        
        if not livro_en:
            print(f"Livro não encontrado no dicionário: {livro_pt}")
            return None 

        # 2. Busca na API
        url = f"https://bible-api.com/{livro_en}+{capitulo_versiculo}?translation=almeida"
        resposta = requests.get(url)
        dados = resposta.json()

        # 3. Processar retorno
        if 'verses' in dados:
            texto_montado = ""
            for v in dados['verses']:
                numero = v['verse']
                texto = v['text'].strip()
                texto_montado += f"**{numero}.** {texto}\n"
            return texto_montado
        
        elif 'text' in dados: 
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
            # Ajuste técnico para link: substitui espaços e dois pontos por barras
            link_ref = ref.replace(' ', '/').replace(':', '/')
            link_backup = f"https://www.bibliaonline.com.br/acf/{link_ref}"
            conteudo = f"_(O texto completo não pôde ser carregado automaticamente.)_\n\n👉 [Clique aqui para ler {ref} online]({link_backup})"
            aviso = "\n\n⚠️ _Abra sua Bíblia física ou use o link acima._"

        mensagem = (
            f"📖 *Leitura do Dia ({hoje})*\n"
            f"📍 *Ref:* `{ref}`\n\n"
            f"{conteudo}"
            f"{aviso}\n\n"
            f"_Bons estudos!_"
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
