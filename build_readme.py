import os
import sys
import json
import urllib.request

# 1. ÂNCORA DE DIRETÓRIO (Padrão CI/CD)
# GITHUB_WORKSPACE garante o caminho para a raiz do repositório.
# O fallback os.getcwd() permite que o script rode localmente na sua máquina para testes.
ROOT_DIR = os.environ.get("GITHUB_WORKSPACE", os.getcwd())

TEMPLATE_FILE = os.path.join(ROOT_DIR, "README_TEMPLATE.md")
OUTPUT_FILE = os.path.join(ROOT_DIR, "README.md")

def fetch_projetos_supabase(url: str, key: str) -> list:
    """Busca os dados dos projetos e garante a integridade da resposta."""
    # O rstrip('/') previne erros caso a URL do GitHub Secrets tenha uma barra no final
    endpoint = f"{url.rstrip('/')}/rest/v1/project_analysis_entity?select=id,titulo,resumo"
    
    req = urllib.request.Request(endpoint)
    req.add_header("apikey", key)
    req.add_header("Authorization", f"Bearer {key}")
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            # Fail-Fast: Se a API retornar uma mensagem de erro em vez de lista, interrompe
            if not isinstance(data, list):
                print(f"ERRO DE INTEGRIDADE: O Supabase retornou um formato inesperado: {data}")
                sys.exit(1)
            return data
    except Exception as e:
        print(f"ERRO DE COMUNICAÇÃO: Falha na requisição ao Supabase. Detalhes: {e}")
        sys.exit(1)

def generate_html_grid(projetos: list) -> str:
    """Monta a grade de cards dinamicamente."""
    if not projetos:
        return "<p>Nenhum projeto encontrado no momento.</p>"

    html = "<table>\n  <tr>\n"
    for index, proj in enumerate(projetos):
        if index > 0 and index % 2 == 0:
            html += "  </tr>\n  <tr>\n"
            
        repo_id = proj.get('id', '')
        titulo = proj.get('titulo', 'Projeto Sem Título')
        resumo = proj.get('resumo', '')
        
        github_url = f"https://github.com/LeCo851/{repo_id}" if repo_id else "https://github.com/LeCo851"
        
        html += f"""    <td width="50%" valign="top" align="center">
      <h4>{titulo}</h4>
      <p>{resumo}</p>
      <br><br>
      <a href="{github_url}">Ver Repositório</a>
    </td>\n"""
        
    html += "  </tr>\n</table>"
    return html

def update_readme_file(html_content: str):
    """Substitui o placeholder no template e salva o arquivo final de forma segura."""
    # 2. VALIDAÇÃO DE ESTADO (Verificação explícita do arquivo)
    if not os.path.exists(TEMPLATE_FILE):
        print(f"ERRO CRÍTICO: O template não foi encontrado em {TEMPLATE_FILE}")
        print(f"Conteúdo da raiz do repositório: {os.listdir(ROOT_DIR)}")
        sys.exit(1)

    with open(TEMPLATE_FILE, "r", encoding="utf-8") as file:
        template_content = file.read()
        
    final_content = template_content.replace("{{PROJETOS_SUPABASE}}", html_content)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        file.write(final_content)

def main():
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("ERRO CRÍTICO: Variáveis SUPABASE_URL ou SUPABASE_KEY ausentes no ambiente.")
        sys.exit(1)
        
    print("Iniciando rotina de automação do README...")
    projetos = fetch_projetos_supabase(supabase_url, supabase_key)
    html_grid = generate_html_grid(projetos)
    update_readme_file(html_grid)
    
    print("Processo finalizado com sucesso! README atualizado.")

if __name__ == "__main__":
    main()
