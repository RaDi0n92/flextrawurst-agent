from agent.dak_gord_system.graf import graf
from agent.dak_gord_system.zustand import Bauzustand

if __name__ == "__main__":
    text = input("Was soll dak+gord-system bauen?\n> ").strip()
    zustand = Bauzustand(nutzer_text=text)
    ergebnis = graf.invoke(zustand)

    print("\n=== PLAN ===")
    for zeile in ergebnis.plan:
        print(zeile)

    if ergebnis.verfassungs_warnungen:
        print("\n=== VERFASSUNGS-WARNUNGEN ===")
        for w in ergebnis.verfassungs_warnungen:
            print("-", w)

    print("\n=== PATCH ===")
    print(ergebnis.patch)
