import getpass
import os
import json
from pathlib import Path
import time
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

# 1) Carregar variáveis de ambiente do arquivo .env na raiz do projeto
load_dotenv(find_dotenv())

# 2) Configurar o cliente OpenAI apontando para o endpoint do IRLab
api_key = os.environ.get("IRLAB_API_KEY") or getpass.getpass("Token: ")
client = OpenAI(
    api_key=api_key,
    base_url="https://inference.irlab.org/v1"
)

# 3) Definir diretórios e parâmetros globais
carpeta = Path(__file__).resolve().parent
POLL_SECONDS = 15

INSTRUCCION = "Responde solo SI o NO, sin explicaciones."
PREGUNTA = "¿Menciona esta frase alguna enfermedad? Frase: {frase}" 
FRASES = { 
    "f1": "El paciente presenta diabetes de tipo 2.",
    "f2": "La reunión del departamento se ha movido al jueves.", 
    "f3": "Mejoró la función pulmonar tras el tratamiento.",
}

# 4) Gerar o arquivo input.jsonl para o Batch
input_path = carpeta / "input.jsonl"
with open(input_path, "w", encoding="utf-8") as f: 
    for cid, frase in FRASES.items():
        peticion = {
            "custom_id": cid,
            "method": "POST",
            "url": "/v1/chat/completions", 
            "body": {
                "messages": [
                    {"role": "system", "content": INSTRUCCION}, 
                    {"role": "user", "content": PREGUNTA.format(frase=frase)},
                ],
                "max_tokens": 10, 
                "temperature": 0,
            },
        }
        f.write(json.dumps(peticion, ensure_ascii=False) + "\n")

print(f"Arquivo '{input_path.name}' gerado com sucesso.")

# 5) Enviar o arquivo e criar o Batch
with input_path.open("rb") as f:
    subido = client.files.create(file=f, purpose="batch")

batch = client.batches.create(
    input_file_id=subido.id,
    endpoint="/v1/chat/completions",
    completion_window="24h",
)
print(f"Batch {batch.id} enviado. Estado inicial: {batch.status}")

# 6) Aguardar a conclusão do Batch sem saturar o servidor
terminales = {"completed", "failed", "cancelled", "expired"} 
while batch.status not in terminales:
    time.sleep(POLL_SECONDS) 
    batch = client.batches.retrieve(batch.id)
    print(f"Estado atual: {batch.status} | Contagem: {batch.request_counts}")

if batch.status != "completed":
    raise SystemExit(f"O batch terminou com o estado '{batch.status}': {batch.errors}")

# 7) Salvar os resultados em bruto
output_path = carpeta / "output.jsonl"
salida = client.files.content(batch.output_file_id).text 
output_path.write_text(salida, encoding="utf-8") 

if batch.error_file_id:
    errores = client.files.content(batch.error_file_id).text 
    (carpeta / "errors.jsonl").write_text(errores, encoding="utf-8")

print("\n--- Resultados do Processamento ---")
# 8) Processar as respostas obtidas
for linea in salida.splitlines():
    r = json.loads(linea)
    cid = r["custom_id"]
    
    if r.get("error") or r["response"]["status_code"] != 200:
        print(f"{cid}: ERRO -> {r.get('error') or r['response']['body']}")
        continue
        
    cuerpo = r["response"]["body"]
    respuesta = cuerpo["choices"][0]["message"]["content"] 
    print(f"{cid} -> {respuesta.strip()}")