import os
import urllib.request

# Obtiene la ruta raíz del proyecto (un nivel arriba de scripts/)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dest_dir = os.path.join(base_dir, "documentos", "bimbam_buy")
os.makedirs(dest_dir, exist_ok=True)

# URLs y nombres de archivos
documentos = {
    "politica_reembolsos.pdf": "https://cdn1.gnarususercontent.com.br/documents/6/internal/1f8444c5-5e8d-4fdb-9b68-19588fbb2d2a.pdf",
    "programa_afiliados.pdf": "https://cdn1.gnarususercontent.com.br/documents/6/internal/1a6f28a5-5804-40b1-9ce1-b9be2cb95881.pdf",
    "guia_envios.pdf": "https://cdn1.gnarususercontent.com.br/documents/6/internal/e0ded762-5654-4a61-92a2-0b52f8621ab8.pdf",
    "faq_pagos.pdf": "https://cdn1.gnarususercontent.com.br/documents/6/internal/b04b3dca-4723-4148-beb2-5ba9ca1a1460.pdf",
    "manual_garantia.pdf": "https://cdn1.gnarususercontent.com.br/documents/6/internal/d2f49550-1121-4192-9891-faf10c359bb1.pdf"
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

print("Iniciando descarga de documentos de BimBam Buy...")
for filename, url in documentos.items():
    filepath = os.path.join(dest_dir, filename)
    print(f"Descargando {filename}...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            with open(filepath, 'wb') as out_file:
                out_file.write(response.read())
        print(f"-> Guardado en {filepath}")
    except Exception as e:
        print(f"Error al descargar {filename}: {e}")

print("Proceso finalizado.")
