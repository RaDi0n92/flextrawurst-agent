# dak+gord-system – Runbook

## Agent manuell starten
```bash
python3 /root/werkraum/starte_dak_gord_system.py
systemctl list-timers | grep dak-neugier
journalctl -u dak-neugier.service -n 20 --no-pager
tail -n 20 /root/werkraum/agent/dak_gord_system/spuren/neugier_ticker.log
sed -n '1,80p' /root/werkraum/agent/dak_gord_system/spuren/agentdateien/projekt/vision4.agent.md
Dann **KNOWN_ISSUES.md**:

```bash
cat > /root/werkraum/docs/agent/KNOWN_ISSUES.md <<'EOF'
# dak+gord-system – Known Issues

## 1. Langer Modelllauf
Einzelne Antworten können weiterhin langsam sein.

## 2. Chatloop ist nicht die richtige Heimat für Hintergrundarbeit
Neugier wurde deshalb in `dak-neugier.timer` ausgelagert.

## 3. Dossierqualität ist gut, aber sprachliche Verengung bleibt möglich
Der stabile Gesamtstand ist inzwischen kanonisch, kann aber später weiter verfeinert werden.

## 4. Kein explizites zentrales Run-State-Modell
Es gibt Spuren und Dossiers, aber noch keinen klaren LangGraph-AgentState als dokumentierten Standard.

## 5. Keine echte Approval-Schicht
Riskante Aktionen werden noch nicht systematisch unterbrochen und freigegeben.

## 6. Keine Eval-Suite
Es fehlt ein definierter Satz von Agententests.

## 7. Kein sauber dokumentierter Resume-Mechanismus für Gesprächs-/Taskläufe
Gedächtnis ist da, aber echte Run-Wiederaufnahme ist noch nicht formalisiert.
