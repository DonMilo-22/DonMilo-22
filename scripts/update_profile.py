import html
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

OWNER = "DonMilo-22"
PROFILE_REPO = "DonMilo-22"
README = Path("README.md")
ASSETS = Path("assets")
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

COLORS = ["#8B5CF6","#22D3EE","#F59E0B","#10B981","#F43F5E","#3B82F6","#A78BFA","#14B8A6","#F97316","#84CC16","#EC4899"]

def api(url, accept="application/vnd.github+json"):
    headers = {"Accept": accept, "User-Agent": "dynamic-profile-readme"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.load(response)

def graphql(query, variables=None):
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is required")
    payload = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
    req = urllib.request.Request("https://api.github.com/graphql", data=payload, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json", "User-Agent": "dynamic-profile-readme"}, method="POST")
    with urllib.request.urlopen(req, timeout=25) as response:
        body = json.load(response)
    if body.get("errors"):
        raise RuntimeError(body["errors"])
    return body["data"]

def clean(text):
    return " ".join((text or "").replace("|", "\\|").split())

def replace_block(text, start_marker, end_marker, block):
    before, sep, rest = text.partition(start_marker)
    if not sep:
        raise RuntimeError(f"Missing marker: {start_marker}")
    _, sep2, after = rest.partition(end_marker)
    if not sep2:
        raise RuntimeError(f"Missing marker: {end_marker}")
    return before + block + after

def write_activity_svg(commits, prs, issues, repos_count, year, stamp):
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="760" height="190" viewBox="0 0 760 190">
  <rect width="760" height="190" rx="18" fill="#0d1117" stroke="#30363d"/>
  <text x="28" y="38" fill="#f0f6fc" font-family="Arial, sans-serif" font-size="20" font-weight="700">GitHub activity · {year}</text>
  <text x="28" y="62" fill="#8b949e" font-family="Arial, sans-serif" font-size="12">Updated automatically · {html.escape(stamp)}</text>
  <g font-family="Arial, sans-serif">
    <rect x="28" y="84" width="160" height="76" rx="14" fill="#161b22" stroke="#30363d"/>
    <text x="44" y="108" fill="#8b949e" font-size="12">COMMITS</text>
    <text x="44" y="143" fill="#a78bfa" font-size="30" font-weight="700">{commits}</text>
    <rect x="208" y="84" width="160" height="76" rx="14" fill="#161b22" stroke="#30363d"/>
    <text x="224" y="108" fill="#8b949e" font-size="12">PULL REQUESTS</text>
    <text x="224" y="143" fill="#22d3ee" font-size="30" font-weight="700">{prs}</text>
    <rect x="388" y="84" width="160" height="76" rx="14" fill="#161b22" stroke="#30363d"/>
    <text x="404" y="108" fill="#8b949e" font-size="12">ISSUES</text>
    <text x="404" y="143" fill="#f59e0b" font-size="30" font-weight="700">{issues}</text>
    <rect x="568" y="84" width="164" height="76" rx="14" fill="#161b22" stroke="#30363d"/>
    <text x="584" y="108" fill="#8b949e" font-size="12">PUBLIC REPOS</text>
    <text x="584" y="143" fill="#10b981" font-size="30" font-weight="700">{repos_count}</text>
  </g>
</svg>"""
    ASSETS.joinpath("github-activity.svg").write_text(svg, encoding="utf-8")

def write_languages_svg(languages, stamp):
    top = languages[:11]
    max_count = max((count for _, count in top), default=1)
    height = 92 + len(top) * 30 + 28
    rows = []
    for i, (language, count) in enumerate(top):
        y = 84 + i * 30
        width = max(14, int(360 * count / max_count))
        color = COLORS[i % len(COLORS)]
        label = html.escape(language)
        rows.append(f'<text x="28" y="{y+12}" fill="#c9d1d9" font-family="Arial, sans-serif" font-size="13">{label}</text>')
        rows.append(f'<rect x="170" y="{y}" width="360" height="14" rx="7" fill="#21262d"/>')
        rows.append(f'<rect x="170" y="{y}" width="{width}" height="14" rx="7" fill="{color}"/>')
        rows.append(f'<text x="548" y="{y+12}" fill="#8b949e" font-family="Arial, sans-serif" font-size="12">{count} repo{"s" if count != 1 else ""}</text>')
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="640" height="{height}" viewBox="0 0 640 {height}">
  <rect width="640" height="{height}" rx="18" fill="#0d1117" stroke="#30363d"/>
  <text x="28" y="38" fill="#f0f6fc" font-family="Arial, sans-serif" font-size="20" font-weight="700">Languages by repository</text>
  <text x="28" y="60" fill="#8b949e" font-family="Arial, sans-serif" font-size="12">Primary language detected by GitHub · {html.escape(stamp)}</text>
  {"".join(rows)}
</svg>"""
    ASSETS.joinpath("languages.svg").write_text(svg, encoding="utf-8")

def main():
    ASSETS.mkdir(exist_ok=True)
    repos = api(f"https://api.github.com/users/{OWNER}/repos?per_page=100&sort=updated")
    repos = [r for r in repos if not r.get("fork") and r.get("name") != PROFILE_REPO and not r.get("archived")]
    repos.sort(key=lambda r: r.get("pushed_at") or r.get("updated_at") or "", reverse=True)
    latest = repos[:8]

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [START, "", "> 🔄 Esta sección se genera automáticamente desde GitHub.", "", "| Proyecto | Lenguaje | Qué hace |", "|---|---|---|"]
    for repo in latest:
        name = repo["name"]
        language = repo.get("language") or "Por detectar"
        description = clean(repo.get("description") or FALLBACKS.get(name) or "Proyecto reciente de mi portafolio.")
        lines.append(f"| [**{name}**]({repo['html_url']}) | `{language}` | {description} |")
    lines += ["", f"<sub>Última sincronización automática: {stamp}</sub>", "", END]
    project_block = "\n".join(lines)

    year = datetime.now(timezone.utc).year
    query = urllib.parse.quote(f"author:{OWNER} committer-date:>={year}-01-01")
    commit_search = api(f"https://api.github.com/search/commits?q={query}&per_page=1", accept="application/vnd.github.cloak-preview+json")
    commits = int(commit_search.get("total_count", 0))

    activity_query = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          totalPullRequestContributions
          totalIssueContributions
        }
      }
    }
    """
    activity = graphql(activity_query, {"login": OWNER, "from": f"{year}-01-01T00:00:00Z", "to": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})["user"]["contributionsCollection"]

    language_counts = {}
    for repo in repos:
        lang = repo.get("language")
        if lang:
            language_counts[lang] = language_counts.get(lang, 0) + 1
    languages = sorted(language_counts.items(), key=lambda item: (-item[1], item[0].lower()))

    write_activity_svg(commits, activity["totalPullRequestContributions"], activity["totalIssueContributions"], len(repos), year, stamp)
    write_languages_svg(languages, stamp)

    text = README.read_text(encoding="utf-8")
    text = replace_block(text, START, END, project_block)
    README.write_text(text, encoding="utf-8")

if __name__ == "__main__":
    main()