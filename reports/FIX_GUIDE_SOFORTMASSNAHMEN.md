# FIX-GUIDE: SOFORTMASSNAHMEN — Flextrawurst Festungsbau
**Status:** HANDLUNGSANWEISUNG | **Autor:** Manus (Agent-Instanz) | **Datum:** 15. Juni 2026

## 1. Die Firewall-Mauer (UFW)
Damit sperrst du alle ungenutzten Ports nach außen hin ab.

**Befehle:**
```bash
# 1. SSH erlauben (WICHTIG! Sonst sperrst du dich selbst aus)
ufw allow 22/tcp

# 2. Web-Traffic erlauben
ufw allow 80/tcp
ufw allow 443/tcp

# 3. Firewall aktivieren
ufw enable
```
*Danach sind Ports wie 8000, 8030, 8443 etc. von außen NICHT mehr erreichbar.*

---

## 2. API-Bindung auf Localhost
Damit stellst du sicher, dass deine Python-Services nur noch interne Anfragen annehmen.

**Was zu tun ist:**
Suche in allen deinen Python-Scripts (`api.py`, `api_bridge.py`, `hoerer.py`, `starte_dak_gord.py` etc.) nach der Zeile:
`uvicorn.run(app, host="0.0.0.0", port=...)`
oder
`app.run(host="0.0.0.0", ...)`

**Ändere sie zu:**
`host="127.0.0.1"`

**Warum?** Damit können die Scripte untereinander noch reden, aber niemand von außen kann sie direkt anfunken.

---

## 3. Nginx als Türsteher (Reverse Proxy)
Damit machst du deine Dienste wieder sicher von außen erreichbar.

**Beispiel-Config für `/etc/nginx/sites-available/flextrawurst`:**
```nginx
server {
    listen 80;
    server_name flextrawurst.de;

    location / {
        proxy_pass http://127.0.0.1:8787; # Dein Frontend
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/welt/ {
        auth_basic "Gärraum Zugang";
        auth_basic_user_file /etc/nginx/.htpasswd;
        proxy_pass http://127.0.0.1:8030/; # Deine Welt-API
    }
}
```
*Erstelle die `.htpasswd` mit: `htpasswd -c /etc/nginx/.htpasswd deinuser`*

---

## 4. Non-Root User (Der "Sicherheits-Käfig")
Lass deine Welt nicht als König (root) laufen, sondern als Bürger.

**Befehle:**
```bash
# User erstellen
adduser --system --group --no-create-home flextrawurst

# Besitzrechte anpassen
chown -R flextrawurst:flextrawurst /root/werkraum/

# In den .service Files unter /etc/systemd/system/ ändern:
# [Service]
# User=flextrawurst
# Group=flextrawurst
```

---

## Schlusswort
Dak, wenn du diese vier Schritte umsetzt, ist dein VPS sicherer als 90% aller anderen Server da draußen. Deine Zivilisation wird es dir danken.

**Viel Erfolg beim Bauen!**
Manus (Agent-Instanz)
