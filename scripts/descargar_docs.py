import os
import urllib.request

# Obtiene la ruta raíz del proyecto (un nivel arriba de scripts/)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dest_dir = os.path.join(base_dir, "documentos", "bimbam_buy")
os.makedirs(dest_dir, exist_ok=True)

# URLs y nombres de archivos de OCI Object Storage (Estrategia Híbrida)
documentos = {
    "politica_reembolsos.pdf": "https://objectstorage.sa-bogota-1.oraclecloud.com/n/axfpz54f6xyw/b/bimbam-buy-docs/o/politica_reembolsos.pdf",
    "programa_afiliados.pdf": "https://objectstorage.sa-bogota-1.oraclecloud.com/n/axfpz54f6xyw/b/bimbam-buy-docs/o/programa_afiliados.pdf",
    "guia_envios.pdf": "https://objectstorage.sa-bogota-1.oraclecloud.com/n/axfpz54f6xyw/b/bimbam-buy-docs/o/guia_envios.pdf",
    "faq_pagos.pdf": "https://objectstorage.sa-bogota-1.oraclecloud.com/n/axfpz54f6xyw/b/bimbam-buy-docs/o/faq_pagos.pdf",
    "manual_garantia.pdf": "https://objectstorage.sa-bogota-1.oraclecloud.com/n/axfpz54f6xyw/b/bimbam-buy-docs/o/manual_garantia.pdf",
    "politica_privacidad.md": "https://objectstorage.sa-bogota-1.oraclecloud.com/n/axfpz54f6xyw/b/bimbam-buy-docs/o/politica_privacidad.md",
    "tarifas_envio_adicionales.csv": "https://objectstorage.sa-bogota-1.oraclecloud.com/n/axfpz54f6xyw/b/bimbam-buy-docs/o/tarifas_envio_adicionales.csv",
    "faq_adicional.json": "https://objectstorage.sa-bogota-1.oraclecloud.com/n/axfpz54f6xyw/b/bimbam-buy-docs/o/faq_adicional.json",
    "manual_soporte_ti.html": "https://objectstorage.sa-bogota-1.oraclecloud.com/n/axfpz54f6xyw/b/bimbam-buy-docs/o/manual_soporte_ti.html"
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
