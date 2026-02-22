import os
import sys
import json
import urllib.request

# Diretório raiz do repositório (funciona no GitHub Actions)
ROOT_DIR = os.environ.get("GITHUB_WORKSPACE", os.getcwd())

OUTPUT_FILE = os.path.join(ROOT_DIR, "README.md")


def get_template_path():
    """
    Procura README_TEMPLATE.md ignorando case sensitivity.
    Funciona mesmo em ambiente Linux (GitHub Actions).
    """
    print("🔎 Procurando template dentro de:", ROOT_DIR)

    files = os.listdir(ROOT_DIR)
    print("📂 Arquivos encontrados:", files)

    for filename in files:
        if filename.lower() == "readme_template.md":
            template_path = os.path.join(ROOT_DIR, filename)
            print("✅ Template encontrado:", template_path)
            return template_path

    print("❌ ERRO CRÍTICO: README_TEMPLATE.md não encontrado.")
    sys.exit(1)


def fetch_projetos_supabase(url: str, key: str) -> list:
    endpoint = f"{url.rstrip('/')}/rest/v1/project_analysis_entity?select=id,titulo,resumo"

    req = urllib.request.Request(endpoint)
    req.add_header("apikey", key)
    req.add_header("Authorization", f"Bearer {key}")

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))

            if not isinstance(data, list):
                print("❌ Supabase retornou formato inesperado:", data)
                sys.exit(1)

            return data

    except Exception as e:
        print("❌ ERRO AO CONSULTAR SUPABASE:", e)
        sys.exit(1)


def generate_html_grid(projetos: list) -> str:
    if not projetos:
        return "<p>Nenhum projeto encontrado.</p>"

    html = "<table>\n  <tr>\n"

    for index, proj in enumerate(projetos):
        if index > 0 and index % 2 == 0:
            html += "  </tr>\n  <tr>\n"

        repo_id = proj.get("id", "")
        titulo = proj.get("titulo", "Projeto Sem Título")
        resumo = proj.get("resumo", "")

        github_url = (
            f"https://github.com/LeCo851/{repo_id}"
            if repo_id
            else "https://github.com/LeCo851"
        )

        html += f"""    <td width="50%" valign="top" align="center">
      <h4>{titulo}</h4>
      <p>{resumo}</p>
      <br><br>
      <a href="{github_url}">Ver Repositório</a>
    </td>\n"""

    html += "  </tr>\n</table>"
    return html


def update_readme_file(html_content: str):
    template_path = get_template_path()

    with open(template_path, "r", encoding="utf-8") as file:
        template_content = file.read()

    final_content = template_content.replace(
        "{{PROJETOS_SUPABASE}}",
        html_content
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        file.write(final_content)

    print("✅ README.md atualizado com sucesso!")


def main():
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("❌ ERRO: Variáveis SUPABASE_URL ou SUPABASE_KEY ausentes.")
        sys.exit(1)

    print("🚀 Buscando dados no Supabase...")
    projetos = fetch_projetos_supabase(supabase_url, supabase_key)

    print("🧱 Gerando HTML...")
    html_grid = generate_html_grid(projetos)

    print("📝 Atualizando README...")
    update_readme_file(html_grid)

    print("🎉 Processo finalizado com sucesso!")


if __name__ == "__main__":
    main()
