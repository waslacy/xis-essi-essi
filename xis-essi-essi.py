import yaml
import argparse

# ===== Carrega yaml =====
def load_config(path="config.yaml"):
  with open(path, "r") as file:
    return yaml.safe_load(file)
  

# ===== Carrega lista de payloads =====
def load_payloads(payload_file):
  with open(payload_file, "r") as file:
    return [line.strip() for line in file if line.strip()]
  
  
# ===== Main =====  
if __name__ == "__main__":
  config = load_config()
  
  # CLI args
  parser = argparse.ArgumentParser(description="XSS Scanner (xis-essi-essi!)")
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