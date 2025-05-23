import yaml
import argparse
import sys
import asyncio
from crawler import crawl
from injector import injector

# ===== Loads yaml =====
def load_config(path="config.yaml"):
	try:
		with open(path, "r") as file:
			return yaml.safe_load(file)
	except Exception as e:
		print(f"[!] Fail to load config.yaml: {e}")
		sys.exit(1)


# ===== Load payloads list =====
def load_payloads(payload_file):
	try:
		with open(payload_file, "r") as file:
			return [line.strip() for line in file if line.strip()]

	except FileNotFoundError:
		print(f"[!] File Not Found: {payload_file}")
		sys.exit(1)


# ===== Banner screen =====
def show_banner(mode):
    print("""
╔════════════════════════════════════════════════════╗
║             Xis Essi Essi - XSS Scanner            ║
║        Scanner simples e extensível para XSS       ║
║     Desenvolvido para fins educacionais e testes   ║
╚════════════════════════════════════════════════════╝
""")
    if mode == "full": 
        print("""Uso:
    python3 xis-essi-essi.py -u "https://alvo.com"

Opções:
    -u / --url        Site alvo para teste (obrigatório)
    -p / --payloads   Caminho para o arquivo de payloads (opcional, arquivo padrão no yaml)
""")


# ===== Modify ArgumentParser to add the banner on -h =====
class CustomArgumentParser(argparse.ArgumentParser):
    def print_help(self, file=None):
        show_banner("basic")
        super().print_help(file)
        

async def main():
    config = load_config()

    if len(sys.argv) == 1:
        show_banner("full")
        sys.exit(0)

    # CLI args
    parser = CustomArgumentParser(description="XSS Scanner (xis-essi-essi!)")
    parser.add_argument("-u", "--url", required=True, help="Target Site")
    parser.add_argument("-p", "--payloads", default=config.get("payloads_file", "payloads.txt"), help="Payloads list")
    args = parser.parse_args()

    # YAML params
    headers = {
        "User-Agent": config["user_agent"]
    }
    delay = config.get("delay_between_requests", 1)
    use_browser = config.get("use_headless_browser", False)
    depth = config.get("max_depth", 3)
    num_threads = config.get("num_threads", 3)

    # load payloads
    payloads = load_payloads(args.payloads)

    # run URL crawler
    exploitable_urls = await crawl(args.url, depth, delay, headers)

    print("[!] Iniciando injector [!]")
    vulnerable_urls = await injector(exploitable_urls, payloads, headers)
    print(vulnerable_urls)

# ===== Main =====  
if __name__ == "__main__":
    asyncio.run(main())