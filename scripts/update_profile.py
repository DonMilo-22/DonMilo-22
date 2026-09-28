import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

OWNER = "DonMilo-22"
PROFILE_REPO = "DonMilo-22"
README = Path("README.md")
START = "<!-- AUTO:RECENT_PROJECTS_START -->"
END = "<!-- AUTO:RECENT_PROJECTS_END -->"

FALLBACKS = {
    "BaseDeTareas": "Plataforma para organizar clases, tareas, anuncios, calendario y recordatorios.",
    "Atlas-MX": "Experiencia interactiva para explorar destinos, cultura y gastronomía de México.",
    "TaskFlow-CLI": "Administrador de tareas local desde terminal construido con TypeScript.",
    "GoLink-Checker": "Comprobador concurrente de URLs y tiempos de respuesta escrito en Go.",
    "Cpp-System-Monitor": "Monitor ligero de recursos del sistema escrito en C++.",
    "Kotlin-Expense-Tracker": "Registro local de gastos y resúmenes mensuales hecho con Kotlin.",
    "React-Study-Dashboard": "Dashboard académico local-first para tareas y progreso de estudio.",
    "Windows-Health-Toolkit": "Kit de diagnóstico rápido de Windows creado con PowerShell.",
    "Rust-File-Organizer": "Organizador seguro de archivos por categorías escrito en Rust.",
    "Java-Password-Vault": "Bóveda local educativa con cifrado AES-GCM hecha en Java.",
    "CSharp-Inventory-Manager": "Gestor de inventario CRUD con persistencia JSON en C#.",
    "PHP-URL-Shortener": "Acortador de URLs pequeño y funcional con PHP y SQLite.",
}

def api(url):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "dynamic-profile-readme"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response)

def clean(text):
    return " ".join((text or "").replace("|", "\\|").split())

def main():
    repos = api(f"https://api.github.com/users/{OWNER}/repos?per_page=100&sort=updated")
    repos = [r for r in repos if not r.get("fork") and r.get("name") != PROFILE_REPO and not r.get("archived")]
    repos.sort(key=lambda r: r.get("pushed_at") or r.get("updated_at") or "", reverse=True)
    latest = repos[:8]

    lines = [START, "", "> 🔄 Esta sección se genera automáticamente desde GitHub.", "", "| Proyecto | Lenguaje | Qué hace |", "|---|---|---|"]
    for repo in latest:
        name = repo["name"]
        language = repo.get("language") or "Por detectar"
        description = clean(repo.get("description") or FALLBACKS.get(name) or "Proyecto reciente de mi portafolio.")
        lines.append(f"| [**{name}**]({repo['html_url']}) | `{language}` | {description} |")

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines += ["", f"<sub>Última sincronización automática: {stamp}</sub>", "", END]
    block = "\n".join(lines)

    text = README.read_text(encoding="utf-8")
    before, sep, rest = text.partition(START)
    if not sep:
        raise RuntimeError("No se encontró el marcador inicial en README.md")
    _, sep2, after = rest.partition(END)
    if not sep2:
        raise RuntimeError("No se encontró el marcador final en README.md")
    README.write_text(before + block + after, encoding="utf-8")

if __name__ == "__main__":
    main()