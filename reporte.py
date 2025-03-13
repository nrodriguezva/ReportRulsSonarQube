import json
from playwright.sync_api import sync_playwright

# Cargar el JSON desde un archivo
with open("reglas.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Construir contenido HTML
html_content = """
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        h1 { color: blue; text-align: center; }
        h2 { color: darkred; }
        h3 { color: darkblue; }
        p { font-size: 14px; line-height: 1.6; }
        .severity { font-weight: bold; color: green; }
    </style>
</head>
<body>
    <h1>Reporte de Reglas</h1>
"""

# Recorrer reglas y agregar contenido al HTML solo si el status es "READY"
for rule in data.get("rules", []):
    rule_name = rule.get("name", "Sin nombre")
    rule_key = rule.get("key", "Sin clave")
    severity = rule.get("severity", "Desconocido")
    status = rule.get("status", "").upper()

    # Validar si el status es "READY"
    if status == "READY":
        html_content += f"""
        <h2>{rule_name} ({rule_key})</h2>
        <p class="severity">Severidad: {severity}</p>
        """

        # Agregar secciones de descripción
        for section in rule.get("descriptionSections", []):
            section_key = section.get("key", "").capitalize()
            section_content = section.get("content", "No hay contenido")

            html_content += f"<h3>{section_key}</h3><p>{section_content}</p>"

html_content += "</body></html>"

# Guardar HTML en un archivo
html_filename = "reporte.html"
with open(html_filename, "w", encoding="utf-8") as file:
    file.write(html_content)

# Convertir HTML a PDF con Playwright
pdf_filename = "outputSalida.pdf"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(f"file:///{html_filename}")
    page.pdf(path=pdf_filename)
    browser.close()

print(f" PDF generado con éxito: {pdf_filename}")
