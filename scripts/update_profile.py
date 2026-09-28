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
ACTIVITY_START = "<!-- AUTO:ACTIVITY_START -->"
ACTIVITY_END = "<!-- AUTO:ACTIVITY_END -->"

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

def graphql(query, variables=None):
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is required for GraphQL activity data")
    payload = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "dynamic-profile-readme",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        body = json.load(response)
    if body.get("errors"):
        raise RuntimeError(body["errors"])
    return body["data"]

def replace_block(text, start_marker, end_marker, block):
    before, sep, rest = text.partition(start_marker)
    if not sep:
        raise RuntimeError(f"No se encontró el marcador inicial: {start_marker}")
    _, sep2, after = rest.partition(end_marker)
    if not sep2:
        raise RuntimeError(f"No se encontró el marcador final: {end_marker}")
    return before + block + after

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

    # GitHub activity for the current calendar year.
    year = datetime.now(timezone.utc).year
    activity_query = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          totalCommitContributions
          totalPullRequestContributions
          totalIssueContributions
          totalPullRequestReviewContributions
        }
      }
    }
    """
    activity = graphql(activity_query, {
        "login": OWNER,
        "from": f"{year}-01-01T00:00:00Z",
        "to": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    })["user"]["contributionsCollection"]

    # Count repositories by their primary language. This updates as GitHub re-detects languages.
    language_counts = {}
    for repo in repos:
        lang = repo.get("language")
        if lang:
            language_counts[lang] = language_counts.get(lang, 0) + 1
    languages = sorted(language_counts.items(), key=lambda item: (-item[1], item[0].lower()))

    activity_lines = [
        ACTIVITY_START,
        "",
        "<div align=\"center\">",
        f"  <img src=\"https://img.shields.io/badge/Commits_{year}-{activity['totalCommitContributions']}-8B5CF6?style=for-the-badge&logo=git&logoColor=white\" alt=\"Commits del año\" />",
        f"  <img src=\"https://img.shields.io/badge/Pull_Requests-{activity['totalPullRequestContributions']}-22D3EE?style=for-the-badge&logo=github&logoColor=white\" alt=\"Pull requests del año\" />",
        f"  <img src=\"https://img.shields.io/badge/Issues-{activity['totalIssueContributions']}-F59E0B?style=for-the-badge&logo=github&logoColor=white\" alt=\"Issues del año\" />",
        "</div>",
        "",
        "### 🧬 Lenguajes por repositorio",
        "",
        "| Lenguaje | Repositorios |",
        "|---|---:|",
    ]
    for language, count in languages:
        activity_lines.append(f"| **{language}** | {count} |")
    activity_lines += [
        "",
        "> Los lenguajes se calculan usando el lenguaje principal que GitHub detecta en cada repositorio público propio.",
        "",
        f"<sub>Datos sincronizados: {stamp}</sub>",
        "",
        ACTIVITY_END,
    ]
    activity_block = "\n".join(activity_lines)

    text = README.read_text(encoding="utf-8")
    text = replace_block(text, START, END, block)
    text = replace_block(text, ACTIVITY_START, ACTIVITY_END, activity_block)
    README.write_text(text, encoding="utf-8")

if __name__ == "__main__":
    main()