import json
import requests
from playwright.sync_api import sync_playwright

# Configuración de SonarQube
SONAR_URL = "http://localhost:9000/api/rules/search"
SONAR_TOKEN = "sqa_ec70402908a851a3082005c2e10ccbbf597a5c19"  # Reemplaza con tu token de SonarQube
LANGUAGES = ["java", "html", "javascript"]  # Lista de lenguajes a consultar
PAGE_SIZE = 500  # Número de reglas por página

# Función para obtener reglas de SonarQube con autenticación y paginación
def fetch_sonar_rules(language):
    rules = []
    page = 1

    headers = {
        "Authorization": f"Bearer {SONAR_TOKEN}"
    }
    
    while True:
        print(f" Obteniendo reglas para {language} - Página {page}...")
        response = requests.get(SONAR_URL, params={"languages": language, "ps": PAGE_SIZE, "p": page}, headers=headers)
        
        if response.status_code != 200:
            print(f" Error al obtener reglas para {language}: {response.status_code} - {response.text}")
            break
        
        data = response.json()
        
        if "rules" not in data:
            print(f" No se encontraron reglas para {language}")
            break

        # Filtrar solo reglas con status "READY"
        filtered_rules = [rule for rule in data["rules"] if rule.get("status", "").upper() == "READY"]
        rules.extend(filtered_rules)

        # Si ya no hay más páginas, terminamos
        if page * PAGE_SIZE >= data.get("total", 0):
            break

        page += 1

    return rules

# Construir contenido HTML
html_content = """
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            padding: 1,3cm; /* Márgenes de 2 cm */
        }
        h1 { color: blue; text-align: center; }
        h2 { color: darkred; }
        h3 { color: darkblue; }
        p { font-size: 14px; line-height: 1.6; }
        .severity { font-weight: bold; color: green; }
        .section-title { font-weight: bold; font-style: italic; }
        .page-number { position: fixed; bottom: 10px; right: 10px; font-size: 12px; }
        .toc { margin-bottom: 20px; padding: 10px; border: 1px solid #ccc; background-color: #f9f9f9; }
        .toc a { text-decoration: none; color: blue; font-weight: bold; }
        .toc a:hover { text-decoration: underline; }
        .rule { border-bottom: 1px solid #ccc; padding-bottom: 10px; margin-bottom: 10px; }
    </style>
</head>
<body>
    <h1>Reporte de Reglas de SonarQube</h1>

    <div class="toc">
        <h2>Tabla de Contenido</h2>
"""

# Agregar tabla de contenido con enlaces a cada lenguaje
for language in LANGUAGES:
    html_content += f'<p><a href="#{language}">{language.upper()}</a></p>'

html_content += "</div>"

# Obtener reglas de todos los lenguajes
for language in LANGUAGES:
    rules = fetch_sonar_rules(language)

    if rules:
        html_content += f'<h2 id="{language}">{language.upper()}</h2>'
    
    for rule in rules:
        rule_name = rule.get("name", "Sin nombre")
        rule_key = rule.get("key", "Sin clave")
        severity = rule.get("severity", "Desconocido")
        description_sections = rule.get("descriptionSections", [])

        html_content += f"""
        <div class="rule">
            <h3>{rule_name} ({rule_key})</h3>
            <p class="severity">Severidad: {severity}</p>
        """

        # Agregar las secciones de descripción
        for section in description_sections:
            section_key = section.get("key", "Sin título").capitalize()
            section_content = section.get("content", "No hay contenido disponible")

            html_content += f"""
            <p class="section-title">{section_key}:</p>
            <p>{section_content}</p>
            """

        html_content += "</div>"

html_content += '<div class="page-number">Página <span class="pageNumber"></span></div>'
html_content += "</body></html>"

# Guardar HTML en un archivo
html_filename = "reporte.html"
with open(html_filename, "w", encoding="utf-8") as file:
    file.write(html_content)

# Convertir HTML a PDF con Playwright, agregando números de página
pdf_filename = "outputSalida.pdf"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(f"file:///{html_filename}")

    # Agregar números de página en el PDF
    page.evaluate("""
        () => {
            let pages = document.querySelectorAll('.page-number');
            pages.forEach((el, index) => el.innerText = 'Página ' + (index + 1));
        }
    """)

    # Generar el PDF con tamaño carta y márgenes de 2 cm
    page.pdf(path=pdf_filename, format="letter", margin={"top": "2cm", "bottom": "2cm", "left": "2cm", "right": "2cm"})

    browser.close()

print(f" PDF generado con éxito: {pdf_filename}")
