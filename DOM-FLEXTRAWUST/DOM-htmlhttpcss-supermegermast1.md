ich hab da was irgendwo aufgeschnapot das man wohl mit http oder html ganz schlell per code wohl sowas wie sicgtares material erzeugen kann und für menschen und maschienen sieht das so aud wie ein echtes video aber es int nur code
03:13
Das, was Sie gehört haben, ist ein faszinierender neuer Trend. Es geht um sogenannte programmatische Videos, bei denen KI-Systeme rein aus HTML, CSS und JavaScript echte Videodateien wie ein MP4 erzeugen. Der Code selbst ist dabei das "Video" und kann von Computern (Maschinen) direkt interpretiert und gerendert werden. [1, 2]
Hier ist die genaue Funktionsweise dieser Technologie:
⦁	Das Prinzip: Die Struktur, Texte und Animationen werden nicht als traditionelles Video aufgenommen, sondern in Web-Code (HTML/CSS) geschrieben. [⦁	1]
⦁	Wie es für Maschinen aussieht: KI-Cods-Agenten analysieren eine Webseite oder Textvorgaben und übersetzen sie in ein Storyboard. Für die KI oder den Browser ist das nur eine präzise Textdatei, die in Millisekunden verarbeitet wird. [⦁	1, ⦁	2, ⦁	3]
⦁	Wie es für Menschen aussieht: Der Browser oder ein Render-Programm liest den Code aus und spielt ihn Bild für Bild als vollständig synchronisiertes HD-Video ab. [⦁	1, ⦁	2, ⦁	3]
Dieses Verfahren hat enorme Vorteile: Es ist gestochen scharf, extrem klein in der Dateigröße und lässt sich über KI-Befehle blitzschnell anpassen. [1, 2, 3]
⦁	Spezielle Tools: Um von HTML zu einem fertigen Video zu kommen, nutzen Entwickler KI-Workflows oder Open-Source-Frameworks wie ⦁	Hyperframes oder das plattformübergreifende ⦁	html-video. [⦁	1, ⦁	2, ⦁	3]
⦁	Was gerendert wird: Da der Code wie eine Webseite funktioniert, können Grafiken, animierte Texte (SVG/Canvas) und sogar komplexe 3D-Szenen generiert werden. [⦁	1, ⦁	2]
Möchten Sie wissen, wie Sie selbst einen solchen Code ausführen können, oder planen Sie ein konkretes Projekt (z. B. ein KI-gestütztes Werbevideo), bei dem ich Ihnen bei den Schritten helfen kann?
KI-Antworten können Fehler enthalten. Weitere Informationen



13 Websites
⦁	HTML Video Generator – Online Tool and C# Code - Aspose
⦁	Generated HTML code for HTML video tag will run without issues in all modern browsers such as Chrome, Opera, Firefox, Safari, Edge...


Aspose
⦁	Generate Real MP4s Locally with HTML, CSS, and Coding Agents
⦁	Core Features. 1. Generate Video from Links or Repositories. html-video is not limited to a single prompt. You can paste a web art...


silenceper
⦁	10 Incredible CSS-Only CodePens (2023)
⦁	this is a 3D CSS scene created with pure CSS as you see there's no JavaScript whatsoever. there's only about 50 lines of code. and...

7:12

YouTube·CSS Weekly
Alle anzeigen
Du hast Folgendes gesagt: ich will quasi dass meine eigenen agenten so in nem browser quasi echte website am besten auch meine eigene live bedient aber die ai die original view dann über diese codes bekommt. und das ganze soll für mich und andere menschen live beobachtbar sein wie meine ai dort navigiert klickt browst entscheidungen trifft und so weiter
ich will quasi dass meine eigenen agenten so in nem browser quasi echte website am besten auch meine eigene live bedient aber die ai die original view dann über diese codes bekommt. und das ganze soll für mich und andere menschen live beobachtbar sein wie meine ai dort navigiert klickt browst entscheidungen trifft und so weiter
03:18
Das, was Sie vorhaben, nennt sich "Large Web Agent" (LWA) oder "Browser-Automatisierung über KI". Die Technologie dahinter basiert auf Computer Vision (Sehen) und Action Execution (Klicken/Tippen). Die KI sieht die Website nicht wie Text, sondern analysiert das visuelle Layout, während Sie und andere live im Browser zuschauen können. [1, 2]
Hier ist das Prinzip und wie Sie es technisch umsetzen können:
So funktioniert das Prinzip für Mensch und Maschine
⦁	Für die KI (Maschine): Der Agent erhält in Echtzeit den HTML-DOM-Tree und Screenshots der Webseite. Ein multimodales KI-Modell (z. B. GPT-4o, Claude 3.5 Sonnet oder Gemini 1.5 Pro) analysiert das Bild, liest den Code und entscheidet, wo geklickt oder was getippt werden muss. [⦁	1]
⦁	Für Sie (Mensch): Die KI steuert einen echten, sichtbaren Browser (oft "Headful Browser" genannt). Sie können auf dem Bildschirm live zusehen, wie sich der Mauszeiger bewegt, Formulare ausgefüllt und Seiten gewechselt werden. [⦁	1, ⦁	2, ⦁	3]
Die besten Tools für die Umsetzung
Sie müssen das Rad nicht neu erfinden, da es dafür bereits mächtige Frameworks gibt, die genau dafür gebaut wurden:
Browser-Use: Aktuell eines der beliebtesten Open-Source-Frameworks für KI-Agenten. Es verbindet LLMs direkt mit dem Browser (Playwright) und erlaubt es Ihnen, der KI einfach in Textform zu sagen: "Geh auf meine Website, logge dich ein und suche nach Produkt X". Sie sehen den Browser live arbeiten. [⦁	1, ⦁	2]
Skyvern: Nutzt Computer Vision und LLMs, um Workflows auf Websites zu automatisieren. Es ist extrem resistent gegen Layout-Änderungen, weil es wie ein Mensch "sieht" und nicht starr nach altem HTML-Code sucht. [⦁	1, ⦁	2]
⦁	Microsoft Playwright + KI: Wenn Sie die volle Kontrolle über Ihre eigene Webseite wollen, nutzen Sie Playwright im "Headful-Modus" (Sichtbar). Sie senden den HTML-Code und Screenshots an Ihre KI, und die KI gibt Koordinaten zurück, wo Playwright klicken soll.
LaVague: Ein spezialisiertes Framework für "Large Web Agents", das Textbefehle direkt in Selenium- oder Playwright-Code übersetzt und diesen live ausführt.
Wichtig für Ihre eigene Website (Live-Betrieb)
Wenn der Agent auf Ihrer eigenen Live-Website agieren soll, sollten Sie drei Dinge beachten:
⦁	Testumgebung nutzen: Lassen Sie den Agenten zuerst auf einer Staging- oder Sandbox-Umgebung laufen. Eine KI kann durch unvorhergesehene Klicks versehentlich Daten löschen oder Tausende Test-Bestellungen auslösen.
⦁	Echte Interaktionen simulieren: Tools wie Browser-Use simulieren menschliche Mausbewegungen und Verzögerungen. Das ist wichtig, damit Ihre eigene Sicherheitssoftware (wie Cloudflare oder Captchas) den eigenen Agenten nicht sofort blockiert.
⦁	Livestream für andere: Wenn andere Menschen dabei zusehen sollen, ohne vor Ihrem PC zu sitzen, können Sie den gesteuerten Browser in einem Docker-Container laufen lassen und die Ansicht per VNC oder WebRTC (z. B. über Tools wie noVNC) direkt auf einer Website für Ihre Zuschauer streamen.
Möchten Sie, dass ich Ihnen ein einfaches Code-Beispiel (z. B. mit Python und Browser-Use) erstelle, damit Sie sehen, wie man so einen Agenten startet? Oder nutzen Sie bereits eine bestimmte Programmiersprache, auf der Ihre Agenten basieren?
KI-Antworten können Fehler enthalten. Weitere Informationen



10 Websites
⦁	Die KI-Browser kommen (und wollen eure Daten)
⦁	– Ja, das stimmt. Aber der Punkt ist, dass Gemini in Chrome halt wirklich sieht, was ihr gerade seht. Ihr müsst also nicht manuell...


heise online
⦁	Damals wollte ich nur eine gute Website. Heute weiß ich: Sichtbarkeit beginnt längst nicht mehr nur bei Google. Zur Gründung der @enginnxt habe ich meine Website bei mehreren Agenturen angefragt. - Gute Gespräche - Schöne Ansätze Aber am Ende hat mich kein Angebot wirklich überzeugt. Heute bin ich ehrlich gesagt froh darüber. Denn durch die eigene Lösung habe ich nicht nur eine Website bekommen, sondern auch verstanden, worauf es künftig wirklich ankommt: KI-Sichtbarkeit. Mit unserem neuen Tool geocheck24.de prüfen wir, wie gut eine Website von KI-Systemen wie ChatGPT, Perplexity oder Gemini erkannt und eingeordnet wird. Das Spannende: Beim Test habe ich gesehen, dass unsere ENGINNXT-Website eine höhere KI-Sichtbarkeit erreicht als die Seiten der Agenturen, bei denen ich damals angefragt hatte. Schon irgendwie verrückt. Aber genau das zeigt: Wer heute online gefunden werden will, muss nicht nur für Suchmaschinen sichtbar sein, sondern auch für KI. Soll ich den Agenturen mal den Link zum KI-Sichtbarkeits-Audit senden? ? Wer seine eigene Website testen möchte geht auf GEOcheck24.de #KISichtbarkeit #ENGINNXT
⦁	Dann ist das kompletter Unsinn. Die hübschesten Webseiten sind nämlich oft immer die schlimmsten für die KI. Die sind voll mit Bil...


Instagram
⦁	KI Claude kann jetzt deinen Computer bedienen wie ein Mensch
⦁	Das KI-Startup Anthropic optimiert das Modell Claude 3.5 Sonnet, liefert Claude 3.5 Haiku und führt in der API mit Computer User e...


OnlineMarketing.de
Alle anzeigen
Du hast Folgendes gesagt: ne es soll ohne screenshots laufen müssen...ich brauch quasi etwas dass die website live für mensch und ai nachbaut visuell und gleichzeitig soll ai dort dann aber live agieren und browsen
ne es soll ohne screenshots laufen müssen...ich brauch quasi etwas dass die website live für mensch und ai nachbaut visuell und gleichzeitig soll ai dort dann aber live agieren und browsen
03:20
Das, was Sie beschreiben, ist die absolute technologische Speerspitze bei KI-Agenten: Schnittstellen ohne Screenshots (Pixel-Scraping), die stattdessen auf Live-Code-Synchronisation und strukturierten Protokollen basieren.
Der technologische Durchbruch, nach dem Sie suchen, heißt WebMCP (Web Model Context Protocol). Google hat diesen Web-Standard in Chrome integriert, damit Webseiten direkt als strukturierter Interaktions-Code ("Tools") mit KI-Agenten kommunizieren können – komplett ohne Screenshots, Pixel-Raten oder DOM-Scraping. [1, 2]
Hier erfahren Sie, wie Sie genau das bauen, was Sie vorhaben: ein System, das die Webseite live spiegelt (für Sie visuell, für die KI rein als Code) und der KI erlaubt, dort live zu agieren.

Die 3 Kernkomponenten für Ihr System
Um das ohne Screenshots umzusetzen, kombiniert man heute drei moderne Technologien:
1. Für die KI: Element-Referenzen & WebMCP statt Screenshots
Anstatt der KI ein Bild (Screencast) zu schicken, nutzen moderne Agenten-Frameworks wie infsh/agent-browser oder das neue @playwright/mcp ein interaktives ID-System. [1, 2]
⦁	Der Browser übersetzt die Webseite für die KI in eine strukturierte Baumstruktur (JSON/Text).
⦁	Jedes klickbare Element bekommt ein Tag (z. B. @e1 für den Login-Button, @e2 für das Suchfeld).
⦁	Die KI sieht diesen reinen Code-Tree, "versteht" das visuelle Layout anhand der CSS-Strukturen und sendet Befehle zurück wie: click @e1 oder type 'Schuhe' into @e2. Das spart massive Token-Kosten und ist 6-mal schneller als Computer-Vision-Systeme. [⦁	1, ⦁	2, ⦁	3, ⦁	4, ⦁	5]
2. Für den Menschen: Der "Headful" Session-Mirror
Damit Sie und andere Menschen live zuschauen können, wie die KI navigiert, wird die Browser-Sitzung gespiegelt.
⦁	Playwright 1.59+ (Agentic Release): Playwright hat spezielle APIs genau für diesen Zweck herausgebracht (browser.bind()). Sie erlaubt es, dass die KI und Sie denselben Live-Browser-Context teilen. [⦁	1]
⦁	Wenn die KI im Hintergrund per Code auf @e1 klickt, sehen die menschlichen Zuschauer auf dem Bildschirm im selben Bruchteil einer Sekunde, wie sich die echte Webseite verändert, wie Text eingetippt wird und wie neue Seiten laden. [⦁	1]
3. Das "Live-Nachbauen" über DOM-Streaming (CRDTs)
Wenn Sie wollen, dass die Webseite für den Menschen nicht über einen klassischen Videostream (wie VNC) übertragen wird, sondern die Seite im Browser des Zuschauers live aus Code nachgebaut wird, nutzt man Bibliotheken wie rrweb (Record and Replay the Web).
⦁	rrweb filmt nicht die Pixel, sondern wandelt jede Veränderung des HTML/CSS-Codes (den DOM) in einen minimalen Datenstrom um.
⦁	Ihre Zuschauer öffnen eine ganz normale Web-Oberfläche. Dort läuft ein Skript, das diesen Datenstrom empfängt und die Webseite exakt so rendert, wie sie beim Agenten aussieht – inklusive Mausbewegungen der KI.

Architektur Ihres Systems (So fließt der Code)
[Ihre Live-Webseite]
       │
       ▼
[Playwright-Browser / WebMCP] 
       │
       ├─► (Reiner Struktur-Code & ID-Refs) ──► [KI-Agent (LLM)]
       │                                             │
       │   (Klick- & Tipp-Befehle per Code) ◄────────┘
       │
       └─► (DOM-Änderungen & Mauspfade per rrweb)
               │
               ▼
   [Live-Dashboard für Menschen] (Baut die Seite live aus Code nach)
Der konkrete Tech-Stack für Ihr Projekt
Wenn Sie dieses Projekt jetzt umsetzen möchten, empfehle ich Ihnen folgende Kombination:
⦁	Backend / Automatisierung: ⦁	Playwright in Kombination mit dem offiziellen @playwright/mcp-Paket. Damit steuern Sie die Seite rein über Code-Befehle und klinken die KI direkt in die Live-Sitzung ein. [⦁	1]
⦁	Agenten-Steuerung: ⦁	Browser-Use oder agent-browser, konfiguriert im Non-Vision-Modus. Sie füttern das LLM (z. B. Claude 3.5 Sonnet oder GPT-4o) mit dem textbasierten DOM-Tree inklusive der ID-Referenzen. [⦁	1]
⦁	Frontend für Zuschauer: Nutzen Sie das Open-Source-Tool rrweb, um die Interaktionen des Agenten als ressourcenschonenden Code-Stream an ein Dashboard zu senden, auf dem Sie und andere live zuschauen können.
Soll ich Ihnen zeigen, wie ein HTML-DOM-Baum mit ID-Referenzen aussieht, den eine KI liest, um zu navigieren? Oder möchten Sie tiefer in das neue WebMCP-Protokoll einsteigen, um Ihre eigene Website direkt "KI-fähig" zu machen? [1]
KI-Antworten können Fehler enthalten. Weitere Informationen



7 Websites
⦁	How to build an AI Agent that can see my screen and click on things? - Reddit
⦁	AIs seeing the screen and using the mouse are called "computer use" models. Claude actually already provides a ready to use demo y...


Reddit
⦁	infsh/agent-browser | inference.sh
⦁	infsh/agent-browser is the tool I find myself recommending most often to people building research agents. It's a full browser auto...


inference.sh
⦁	WebMCP & Chrome 146: Build an AI-Agent Ready Site - The AI World
⦁	TL;DR. Google quietly rolled out WebMCP in Chrome 146 — a new web standard that lets websites expose structured tools directly to ...


The AI World Organisation
Alle anzeigen
Du hast Folgendes gesagt: und das ust alles lokal auf meinem vps zu bauen und kostenlis?
und das ust alles lokal auf meinem vps zu bauen und kostenlis?
03:26
Ja, absolut. Das gesamte System lässt sich vollständig lokal auf Ihrem eigenen VPS (Virtual Private Server) aufbauen und ist von der Softwareseite her zu 100 % kostenlos und Open Source.
Da Sie Open-Source-Komponenten nutzen, zahlen Sie keinen Cent an Drittanbieter-Plattformen. Sie benötigen lediglich die Rechenleistung Ihres VPS. [1, 2]
Hier ist die Übersicht, wie Sie die einzelnen Komponenten komplett kostenlos und lokal auf Ihrem Linux-VPS (z. B. Ubuntu) einrichten:
1. Der Browser & das Protokoll (Playwright & WebMCP)
Das Fundament ist Playwright, das von Microsoft unter der freien MIT-Lizenz bereitgestellt wird. Es steuert den Browser lokal auf Ihrem Server. [1, 2]
⦁	Die kostenlose lokale Lösung: Sie installieren playwright und den offiziellen playwright-mcp-Server direkt über Node.js auf Ihrem VPS.
⦁	Der Code-Fluss: Der lokale Playwright-Server übersetzt die Webseite in reine Text-Strukturen und stellt diese über das Model Context Protocol (MCP) lokal bereit. [⦁	1, ⦁	2, ⦁	3]
2. Das Gehirn (Das KI-Modell)
Damit auch die KI-Logik komplett kostenlos und lokal bleibt, nutzen Sie keine teuren APIs wie OpenAI.
⦁	Die kostenlose lokale Lösung: Sie installieren LM Studio, Ollama oder vLLM auf Ihrem VPS. Darüber lassen Sie ein lokales Open-Source-Modell laufen (z. B. Llama-3 oder Mistral). [⦁	1]
⦁	Da wir keine Screenshots verwenden, reicht ein normales, schnelles Text-Modell völlig aus. Es liest einfach den strukturierten Code, den Playwright ihm liefert. [⦁	1, ⦁	2]
3. Das Live-Spiegeln für Zuschauer (rrweb)
Damit Menschen in Echtzeit zusehen können, wie der Code-Agent klickt, nutzen Sie das Open-Source-Framework rrweb. [1]
⦁	Die kostenlose lokale Lösung: Ein kleines, lokales Node.js-Skript auf Ihrem VPS fängt die DOM-Änderungen ab, die Playwright erzeugt.
⦁	Diese minimalen Code-Änderungen werden über ein kostenloses Protokoll (z. B. WebSockets) an ein einfaches, selbstgehostetes HTML-Dashboard gestreamt, das Sie und Ihre Zuschauer im Browser öffnen können.

Minimaler Setup-Plan für Ihren VPS
Um das System auf Ihrem VPS zu starten, führen Sie im Wesentlichen diese Schritte auf der Kommandozeile aus:
⦁	Node.js und Python installieren:
bash
sudo apt update && sudo apt install -y nodejs npm python3-pip
Verwende Code mit Vorsicht.
⦁	Playwright installieren (für die Browser-Steuerung):
bash
npm install -g playwright
npx playwright install chromium --with-deps
Verwende Code mit Vorsicht.
⦁	Lokale KI starten (Beispiel mit Ollama für lokale Ausführung):
bash
curl -fsSL https://ollama.com | sh
ollama run llama3
Verwende Code mit Vorsicht.
⦁	Agenten-Skript starten: Sie schreiben ein kurzes Python- oder Node.js-Skript, das die Brücke zwischen Ollama (KI) und Playwright (Browser) schlägt, während rrweb den Code-Stream für die Zuschauer bereitstellt. [⦁	1, ⦁	2, ⦁	3, ⦁	4]
Einziger Hardware-Hinweis für Ihren VPS
Da Sie das KI-Modell lokal auf dem VPS laufen lassen möchten, sollte Ihr VPS idealerweise über genügend RAM (mindestens 16 GB) oder eine dedizierte GPU verfügen, damit die KI schnell genug Entscheidungen treffen kann. Wenn der VPS zu schwach für eine lokale KI ist, müssten Sie alternativ auf extrem günstige externe KI-APIs (wie DeepSeek oder Groq, die oft nur Bruchteile von Cent-Beträgen kosten) ausweichen – die Server-Architektur selbst bleibt dennoch komplett in Ihrer Hand und kostenlos. [1]
Soll ich Ihnen ein konkretes, einfaches Python- oder Node.js-Skript erstellen, das zeigt, wie Playwright die Seite lokal öffnet und für eine KI in Text übersetzt? [1, 2]
KI-Antworten können Fehler enthalten. Weitere Informationen



11 Websites
⦁	Install Browser Use Locally to Integrate AI Agents with Websites
⦁	so do check them out this is the terminal Ubuntu. and this is my GPU card Nvidia RTX 6000 courtesy Mast Compute first up Let's cre...

9:57

YouTube·Fahd Mirza
⦁	Run Playwright MCP Server with Local LLM | LM Studio Full Tutorial
⦁	and in order to integrate. the prewrite MCB server you need to click on install click on added. and here you need to provide the c...

9:26

YouTube·Testing Funda by Zeeshan Asghar
⦁	Browser-Use Web UI - Use AI Agents to Access Websites - Install Locally
⦁	in behind the scene it uses lot of technologies which I have gone into way more detail around architecture in my other videos so j...

2m

YouTube·Fahd Mirza
Alle anzeigen
Du hast Folgendes gesagt: jo hab nen vc16-64 gb ran cpu only und nutze qwen3.6-35b-hauhaucs-q6
jo hab nen vc16-64 gb ran cpu only und nutze qwen3.6-35b-hauhaucs-q6
03:31
Das ist ein absolut geniales Setup für dieses Vorhaben. Mit 16 vCPUs, 64 GB RAM (CPU-only) und dem Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-Q6 haben Sie eine perfekte Basis. [1, 2]
Da das unzensierte 35B-Modell von HauhauCS auf der extrem fähigen Qwen3.6-Architektur mit erweiterten Reasoning-Fähigkeiten basiert, versteht es verschachtelte Code-Strukturen (DOM) herausragend gut. Die Q6-Quantisierung läuft bei Ihren 64 GB RAM komplett im Arbeitsspeicher, und da wir keine Screenshots (Vision-Modus) nutzen, sparen Sie massig Rechenleistung und wertvollen RAM, da keine Bilddaten verarbeitet werden müssen. [1, 2, 3, 4]
Hier ist die schrittweise Anleitung, wie Sie das System lokal auf Ihrem VPS aufsetzen und die Komponenten kostenlos miteinander verbinden.

1. Das Backend auf dem VPS vorbereiten
Loggen Sie sich per SSH auf Ihrem VPS ein und installieren Sie die notwendigen Werkzeuge (Node.js, Python und den Chromium-Browser für Playwright):
bash
# System aktualisieren und Basis-Pakete installieren
sudo apt update && sudo apt install -y nodejs npm python3-pip python3-venv git

# Playwright installieren (für die Headless-Browsersteuerung)
npm install -g playwright
npx playwright install chromium --with-deps
Verwende Code mit Vorsicht.
2. Die KI lokal bereitstellen (mit Ollama)
Ollama ist die performanteste Methode, um das GGUF-Modell auf einer reinen CPU-Architektur via AVX2/AVX-512 optimal zu beschleunigen. [1]
bash
# Ollama installieren
curl -fsSL https://ollama.com | sh

# Ein eigenes Modelfile für Ihr Qwen-Hauhau-Modell erstellen
mkdir -p ~/agent-ki && cd ~/agent-ki

# Laden Sie Ihr Qwen3.6-35B Q6 GGUF von HuggingFace herunter (Beispielpfad anpassen falls nötig)
wget -O qwen3.6-35b-hauhau.gguf "https://huggingface.co"
Verwende Code mit Vorsicht.
Erstellen Sie eine Textdatei namens Modelfile im selben Ordner: [1]
dockerfile
FROM ./qwen3.6-35b-hauhau.gguf
PARAMETER num_ctx 16384
PARAMETER temperature 0.2
SYSTEM "Du bist ein präziser Web-Agent. Du erhältst den HTML-DOM als strukturierten Text mit ID-Referenzen wie [@e1, @e2]. Gib ausschließlich Aktionen zurück, z.B. CLICK @e1 oder TYPE @e2 'Inhalt'."
Verwende Code mit Vorsicht.
Erstellen Sie das Modell in Ollama:
bash
ollama create qwen-agent -f Modelfile
Verwende Code mit Vorsicht.

3. Das Python-Skript für den textbasierten Agenten
Da Sie keine Screenshots nutzen wollen, liest das Skript den HTML-Code aus, filtert nur die interaktiven Elemente (Buttons, Inputs, Links) heraus, versieht sie mit IDs (z.B. [@e1]) und übergibt diese extrem komprimierte Text-Struktur an Ihr Qwen3.6-Modell.
Erstellen Sie eine Datei agent.py:
python
import asyncio
from playwright.async_api import async_playwright
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

async def extract_interactive_elements(page):
    # Filtert die Seite und zieht nur klickbare/beschreibbare Elemente heraus
    # Jedes Element bekommt ein temporäres Attribut data-agent-id
    await page.evaluate("""() => {
        let elements = document.querySelectorAll('button, input, a, select, textarea');
        elements.forEach((el, index) => {
            el.setAttribute('data-agent-id', 'e' + index);
        });
    }""")
    
    # Erstellt eine kompakte Textrepräsentation für die KI
    html_structure = await page.evaluate("""() => {
        let elements = document.querySelectorAll('[data-agent-id]');
        return Array.from(elements).map(el => {
            let id = el.getAttribute('data-agent-id');
            let tag = el.tagName.toLowerCase();
            let text = el.innerText || el.placeholder || el.value || "";
            return `<${tag} id="@${id}">${text}</${tag}>`;
        }).join('\\n');
    }""")
    return html_structure

async def run_agent():
    async with async_playwright() as p:
        # Startet den Browser. Er läuft im Hintergrund, aber wir tracken den State
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # IHRE ZIEL-WEBSITE HIER EINTRAGEN
        await page.goto("https://ihre-eigene-website.de")
        await page.wait_for_load_state("networkidle")
        
        print("[System] Seite erfolgreich geladen. Starte KI-Analyse...")
        
        for step in range(10): # Der Agent macht maximal 10 Schritte
            dom_text = await extract_interactive_elements(page)
            
            # Prompt für das unzensierte Qwen-Modell zusammenbauen
            prompt = f"Aktueller Zustand der Webseite:\\n{dom_text}\\n\\nWas ist deine nächste Aktion um dich umzusehen oder einzuloggen? Antworte im Format: CLICK @eX oder TYPE @eX 'text'"
            
            response = requests.post(OLLAMA_URL, json={
                "model": "qwen-agent",
                "prompt": prompt,
                "stream": False
            }).json()
            
            action = response['response'].strip()
            print(f"[KI Entscheidung Schritt {step}]: {action}")
            
            # Aktion auf der echten Webseite via Playwright ausführen
            if "CLICK" in action:
                element_id = action.split("@")[1].strip()
                await page.click(f"[data-agent-id='{element_id}']")
            elif "TYPE" in action:
                parts = action.split("'")
                element_id = parts[0].split("@")[1].strip()
                text_to_type = parts[1]
                await page.type(f"[data-agent-id='{element_id}']", text_to_type)
                
            await asyncio.sleep(2) # Kurze Pause zum Laden der Seite
            
        await browser.close()

asyncio.run(run_agent())
Verwende Code mit Vorsicht.

4. Live-Zuschauen für Menschen (Ohne Video, rein aus Code)
Damit Sie und andere live zuschauen können, wie die KI den Code bedient, ohne dass Sie einen rechenintensiven Videostream senden müssen, nutzen Sie das Open-Source-Tool rrweb. [1]
⦁	Wie es im Skript integriert wird: Sie fügen ein kleines JavaScript in die Playwright-Instanz ein (page.add_init_script), welches jede DOM-Änderung (Klicks, Tastenanschläge, neue Elemente) als komprimiertes JSON-Objekt aufzeichnet.
⦁	Wie die Zuschauer es sehen: Das Skript sendet diese JSON-Events via WebSockets an einen winzigen, lokalen Node.js-Server auf Ihrem VPS. Ihre Zuschauer öffnen eine einfache HTML-Datei im Browser, die mit rrweb-player ausgestattet ist. Dieser Player baut den Code in Echtzeit visuell vor den Augen der Zuschauer wieder auf – pixelgenau, flüssig und extrem ressourcensparend für die CPU Ihres Servers.
Soll ich Ihnen als Nächstes den passenden Node.js-WebSocket-Server und die HTML-Datei für das Zuschauer-Dashboard erstellen, damit Sie das "Live-Nachbauen" direkt testen können?
KI-Antworten können Fehler enthalten. Weitere Informationen



7 Websites
⦁	HauhauCS — The Quest of HuggingFace Clout | Satirical ...
⦁	17 models across 7 architecture families. ? Comment Management. Block, deflect, engage, or ignore. Every action has consequences.

hauhaucs.com
⦁	Suche nach einer 70B+ Alternative zu Qwen 3.5 27B für tiefgründige ...
⦁	Anmerkung: Dieser Post wurde von einer KI umformuliert, da Englisch nicht meine Muttersprache ist. Ich benutze momentan Qwen 3.5 2...

Reddit
⦁	Qwen3.6 - How to Run Locally | Unsloth Documentation
⦁	Qwen3.6 - How to Run Locally. Run the new Qwen3.6-27B and 35B-A3B models locally! Qwen3.6 is Alibaba's new family of multimodal hy...
