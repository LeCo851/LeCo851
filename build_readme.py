import os
import json
import urllib.request

# Constantes para os nomes dos arquivos
TEMPLATE_FILE = "README_TEMPLATE.md"
OUTPUT_FILE = "README.md"

def fetch_projetos_supabase(url: str, key: str) -> list:
    """Busca os dados dos projetos na tabela do Supabase."""
    endpoint = f"{url}/rest/v1/projetos?select=*" # Substitua 'projetos' pelo nome real da sua tabela
    
    req = urllib.request.Request(endpoint)
    req.add_header("apikey", key)
    req.add_header("Authorization", f"Bearer {key}")
    
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def generate_html_grid(projetos: list) -> str:
    """Transforma a lista de projetos em uma tabela HTML (Grid 2xN)."""
    html = "<table>\n  <tr>\n"
    
    for index, proj in enumerate(projetos):
        # Quebra a linha a cada 2 cards para formar o grid
        if index > 0 and index % 2 == 0:
            html += "  </tr>\n  <tr>\n"
            
        html += f"""    <td width="50%" valign="top" align="center">
      <h4>{proj.get('titulo', 'Projeto Sem Título')}</h4>
      <p>{proj.get('descricao', '')}</p>
      <br><br>
      <a href="{proj.get('link_github', '#')}">Ver Repositório</a>
    </td>\n"""
        
    html += "  </tr>\n</table>"
    return html

def update_readme_file(html_content: str):
    """Lê o template, substitui a tag pelo conteúdo gerado e salva o README.md."""
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as file:
        template_content = file.read()
        
    final_content = template_content.replace("{{PROJETOS_SUPABASE}}", html_content)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        file.write(final_content)

def main():
    # Recupera as credenciais injetadas pelo GitHub Actions
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("Credenciais do Supabase não encontradas nas variáveis de ambiente.")
        
    print("Buscando dados no Supabase...")
    projetos = fetch_projetos_supabase(supabase_url, supabase_key)
    
    print("Gerando layout HTML...")
    html_grid = generate_html_grid(projetos)
    
    print("Atualizando README.md...")
    update_readme_file(html_grid)
    
    print("Processo concluído com sucesso!")

if __name__ == "__main__":
    main()
