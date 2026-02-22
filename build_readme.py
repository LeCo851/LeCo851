import os
import sys
import json
import urllib.request
import urllib.parse

# Âncora absoluta apontando para a raiz do repositório
ROOT_DIR = os.environ.get("GITHUB_WORKSPACE", os.getcwd())
OUTPUT_FILE = os.path.join(ROOT_DIR, "README.md")

def get_template_path():
    """Busca o arquivo template ignorando Case Sensitivity."""
    for filename in os.listdir(ROOT_DIR):
        if filename.lower() == "readme_template.md":
            return os.path.join(ROOT_DIR, filename)
    print("ERRO CRÍTICO: Template não encontrado.")
    sys.exit(1)

def fetch_projetos_supabase(url: str, key: str) -> list:
    """Busca projetos e faz o JOIN automático com a tabela de tags via PostgREST."""
    endpoint = f"{url.rstrip('/')}/rest/v1/project_analysis_entity?select=id,titulo,resumo,project_analysis_entity_tags(tags)&order=last_update.desc"
    
    req = urllib.request.Request(endpoint)
    req.add_header("apikey", key)
    req.add_header("Authorization", f"Bearer {key}")
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            if not isinstance(data, list):
                print(f"ERRO: Supabase retornou formato inesperado: {data}")
                sys.exit(1)
            return data
    except Exception as e:
        print(f"ERRO DE COMUNICAÇÃO: {e}")
        sys.exit(1)

def gerar_badge_html(tag: str) -> str:
    """Fabrica a badge do Shields.io mapeando cores e logos baseados no nome da tag."""
    tag_lower = tag.lower()
    cor = "1E293B" # Cor padrão (Dark Slate) para tags conceituais (ex: Backend, Finanças)
    logo = ""

    # Dicionário prático para injeção de estilo (Fácil de expandir no futuro)
    if "java" in tag_lower:
        cor = "ED8B00"
        logo = "&logo=openjdk&logoColor=white"
    elif "spring" in tag_lower:
        cor = "6DB33F"
        logo = "&logo=spring&logoColor=white"
    elif "docker" in tag_lower:
        cor = "2496ED"
        logo = "&logo=docker&logoColor=white"
    elif "angular" in tag_lower:
        cor = "DD0031"
        logo = "&logo=angular&logoColor=white"
    elif "python" in tag_lower:
        cor = "3776AB"
        logo = "&logo=python&logoColor=white"
    elif "postgres" in tag_lower or "oracle" in tag_lower or "db" in tag_lower:
        cor = "336791"
        logo = "&logo=databricks&logoColor=white"

    # Encoding seguro para URLs (Shields.io exige underscores no lugar de espaços)
    tag_formatada = urllib.parse.quote(tag.replace("-", "--").replace(" ", "_"))
    
    return f'<img src="https://img.shields.io/badge/{tag_formatada}-{cor}?style=flat-square{logo}" />'

def generate_html_grid(projetos: list) -> str:
    """Monta a grade HTML injetando as badges em cada card."""
    if not projetos:
        return "<p>Nenhum projeto encontrado.</p>"

    html = "<table>\n  <tr>\n"
    for index, proj in enumerate(projetos):
        if index > 0 and index % 2 == 0:
            html += "  </tr>\n  <tr>\n"
            
        repo_id = proj.get('id', '')
        titulo = proj.get('titulo', 'Projeto Sem Título')
        resumo = proj.get('resumo', '')
        
        # Recupera a lista de tags atreladas ao projeto
        tags_list = proj.get('project_analysis_entity_tags', [])
        
        badges_html = ""
        for tag_obj in tags_list:
            nome_tag = tag_obj.get('tags', '')
            if nome_tag:
                badges_html += f" {gerar_badge_html(nome_tag)}"
        
        github_url = f"https://github.com/LeCo851/{repo_id}" if repo_id else "https://github.com/LeCo851"
        
        html += f"""    <td width="50%" valign="top" align="center">
      <h4>{titulo}</h4>
      <p>{resumo}</p>
      <div align="center">
        {badges_html.strip()}
      </div>
      <br>
      <a href="{github_url}">Ver Repositório</a>
    </td>\n"""
        
    html += "  </tr>\n</table>"
    return html

def update_readme_file(html_content: str):
    template_path = get_template_path()
    
    with open(template_path, "r", encoding="utf-8") as file:
        template_content = file.read()
        
    final_content = template_content.replace("{{PROJETOS_SUPABASE}}", html_content)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        file.write(final_content)

def main():
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("ERRO CRÍTICO: Variáveis SUPABASE ausentes.")
        sys.exit(1)
        
    print("Buscando dados no Supabase...")
    projetos = fetch_projetos_supabase(supabase_url, supabase_key)
    
    print("Gerando layout HTML com Badges...")
    html_grid = generate_html_grid(projetos)
    
    print("Atualizando README.md...")
    update_readme_file(html_grid)
    
    print("Processo finalizado com sucesso!")

if __name__ == "__main__":
    main()
