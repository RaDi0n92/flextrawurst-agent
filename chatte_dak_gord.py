from agent.dak_gord_system.ollama_chat import OllamaChat

def lade_text(pfad, ersatz=""):
    try:
        with open(pfad, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ersatz

llm = OllamaChat()

system = lade_text("agent/dak_gord_system/aufforderungen/system.md", "Du bist dak+gord-system.")
verfassung = lade_text("docs/vision/verfassung.md", "")

systemblock = system.strip()
if verfassung.strip():
    systemblock += "\n\nVERFASSUNG:\n" + verfassung.strip()

verlauf = [{"role": "system", "content": systemblock}]

print("dak+gord-system läuft. Zum Beenden: ende")

while True:
    nutzer = input("\nDu:\n> ").strip()

    if nutzer.lower() == "ende":
        print("\n(dak+gord-system beendet)")
        break

    verlauf.append({"role": "user", "content": nutzer})

    try:
        antwort = llm.chat(verlauf, temperatur=0.2)
    except Exception as e:
        print("\n[dak+gord-system FEHLER]")
        print(str(e))
        continue

    verlauf.append({"role": "assistant", "content": antwort})

    print("\n[dak+gord-system]")
    print(antwort)
