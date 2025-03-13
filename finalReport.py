import json
import requests
from playwright.sync_api import sync_playwright

# Configuración de SonarQube
SONAR_URL = "http://localhost:9000/api/rules/search"
TOKEN = "sqa_ec70402908a851a3082005c2e10ccbbf597a5c19"
LANGUAGES = ["js","web"]  # Puedes agregar más lenguajes aquí
PAGE_SIZE = 500

HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}

rules_by_language = {}

# Obtener reglas por lenguaje
for lang in LANGUAGES:
    page_number = 1
    rules_by_language[lang] = []

    while True:
        response = requests.get(f"{SONAR_URL}?languages={lang}&ps={PAGE_SIZE}&p={page_number}", headers=HEADERS)

        if response.status_code != 200:
            break

        data = response.json()
        rules = data.get("rules", [])
        if not rules:
            break

        rules_by_language[lang].extend(rules)

        if len(rules) < PAGE_SIZE:
            break

        page_number += 1

# Generar HTML
html_content = """
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; padding: 1.2cm; margin: 0; }
        h1 { color: blue; text-align: center; }
        h2 { color: darkred; }
        h3 { color: #333; }
        p { font-size: 14px; line-height: 1.6; }
        a { text-decoration: none; color: blue; }
        hr { border: 1px solid #ddd; margin: 20px 0; }
        .toc { border: 1px solid black; padding: 10px; margin: 20px 0; }
        .page-number { text-align: center; font-size: 12px; margin-top: 10px; }
    </style>
</head>
<body>
    <h1>Reporte de Reglas de SonarQube</h1>
    <div class="toc">
        <h2>Tabla de Contenido</h2>
"""

# Tabla de contenido con links
for lang in LANGUAGES:
    html_content += f'<p><a href="#{lang}">{lang.upper()}</a></p>'

html_content += "</div>"

# Agregar las reglas por lenguaje
for lang, rules in rules_by_language.items():
    html_content += f'<h2 id="{lang}">{lang.upper()}</h2>'
    
    for rule in rules:
        html_content += f'<h3>{rule.get("name", "Sin nombre")}</h3>'
        html_content += f'<p><strong>Clave:</strong> {rule.get("key", "N/A")}</p>'
        html_content += f'<p><strong>Severidad:</strong> {rule.get("severity", "N/A")}</p>'
        html_content += f'<p><strong>Impacto:</strong> {rule.get("impact", "N/A")}</p>'
        html_content += f'<p><strong>Descripción:</strong> {rule.get("htmlDescription", "No disponible")}</p>'

        # Agregar descriptionSections si existen
        if "descriptionSections" in rule:
            for section in rule["descriptionSections"]:
                html_content += f'<h4>{section.get("key", "Sección")}</h4>'
                html_content += f'<p>{section.get("content", "Sin contenido")}</p>'

        html_content += "<hr>"

html_content += """
</body></html>
"""

# Generar PDF con numeración de páginas
pdf_filename = "outputReport.pdf"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    
    # Cargar contenido HTML
    page.set_content(html_content)
    
    # Generar PDF con márgenes y numeración
    page.pdf(
        path=pdf_filename,
        format="Letter",
        margin={"top": "1cm", "right": "1.2cm", "bottom": "1.2cm", "left": "1.2cm"},
        display_header_footer=True,
        header_template='',
        footer_template='''
            <div style="width:100%; text-align:center; font-size:10px;">
                Página <span class="pageNumber"></span> de <span class="totalPages"></span>
            </div>
        ''',
        print_background=True
    )
    
    browser.close()

print(f"PDF generado con éxito: {pdf_filename}")
