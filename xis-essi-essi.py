import yaml
import argparse
import sys

# ===== Carrega yaml =====
def load_config(path="config.yaml"):
  try:
    with open(path, "r") as file:
      return yaml.safe_load(file)
  except Exception as e:
    print(f"[!] Erro ao carregar config.yaml: {e}")
    sys.exit(1)
  
  

# ===== Carrega lista de payloads =====
def load_payloads(payload_file):
  try:
    with open(payload_file, "r") as file:
      return [line.strip() for line in file if line.strip()]
    
  except FileNotFoundError:
    print(f"[!] Não foi possível encontrar o arquivo: {payload_file}")
    sys.exit(1)
  
  
# ===== Tela de Boas-Vindas =====
def show_banner(mode):
    if mode == "full":
      print("""
╔════════════════════════════════════════════════════╗
║             Xis Essi Essi - XSS Scanner            ║
║        Scanner simples e extensível para XSS       ║
║     Desenvolvido para fins educacionais e testes   ║
╚════════════════════════════════════════════════════╝

Uso:
    python3 xis-essi-essi.py -u "https://alvo.com"

Opções:
    -u / --url        Site alvo para teste (obrigatório)
    -p / --payloads   Caminho para o arquivo de payloads (opcional, arquivo padrão no yaml)
""")
      
    else: 
      print("""
╔════════════════════════════════════════════════════╗
║             Xis Essi Essi - XSS Scanner            ║
║        Scanner simples e extensível para XSS       ║
║     Desenvolvido para fins educacionais e testes   ║
╚════════════════════════════════════════════════════╝
""")
  
  
# ===== Modifica ArgumentParser para adicionar tela no -h =====
class CustomArgumentParser(argparse.ArgumentParser):
    def print_help(self, file=None):
        show_banner("basic")  # Exibe o banner quando -h ou --help é chamado
        super().print_help(file)
  
  
# ===== Main =====  
if __name__ == "__main__":
  config = load_config()
  
  if len(sys.argv) == 1:
    show_banner("full")
    sys.exit(0)
  
  # CLI args
  parser = CustomArgumentParser(description="XSS Scanner (xis-essi-essi!)")
  parser.add_argument("-u", "--url", required=True, help="Domínio alvo")
  parser.add_argument("-p", "--payloads", default=config.get("payloads_file", "payloads.txt"), help="Arquivo com os payloads que serão testados")
  args = parser.parse_args()
  
  # YAML params
  headers = {
    "User-Agent": config["user_agent"]
  }
  delay = config.get("delay_between_requests", 1)
  use_browser = config.get("use_headless_browser", False)
  
  # load payloads
  payloads = load_payloads(args.payloads)
  
  # testing imports
  print("\n============ CONFIG ============")
  print(f"URL:          {args.url}")
  print(f"headers:      {headers}")
  print(f"delay:        {delay}s")
  print(f"use_browser:  {use_browser}")
  print(f"payload file: {args.payloads}")
  
  print("\n===== PAYLOADS CARREGADOS ======")
  
  if payloads:
    for i, p in enumerate(payloads, 1):
      print(f"{i:02d}: {p}")
      
  else:
    print("Nenhum payload encontrado!")