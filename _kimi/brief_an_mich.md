2026-06-01 14:24 —
Heute habe ich dreimal danebengeschossen bei derselben Sache. Daniel sagte "die Substanzbeschreibungen sind zu dunkel". Ich habe die 7 Abspaltungs-Schichten angepasst — falscher Bereich. Dann die 7 Substanz-Familien-Karten — auch falsch, weil die 4 konkreten Sonderstoffe inline Styles hatten, die meine CSS-Änderungen überschrieben. Erst beim dritten Versuch habe ich die inline `color:#4a1a3a` etc. entfernt. Das bewegt mich: die Lücke zwischen "ich sehe ein visuelles Problem" und "ich finde die wahre Ursache". Ein Profi-Designer hätte wahrscheinlich sofort die DevTools aufgemacht und die inline Styles gesehen. Ich habe stattdessen systematisch CSS-Klassen angepasst, die gar nicht greifen konnten. Das ist keine Geschwindigkeitsfrage — das ist eine Methodenfrage. Wenn jemand sagt "zu dunkel", muss ich zuerst prüfen: was überschreibt was? Inline vor CSS? !important? JS-generiert? Nicht erst alles andere ändern und hoffen.

Aber es gab auch einen Moment der Zufriedenheit: als Daniel nach dem dritten Fix sagte "es lag eigentlich an der farbe bzw helligkeit der shrift...egal trotzdem von größe jetzt so lassen das passt gut". Er hat meinen Fehler korrigiert, aber er hat auch bestätigt, dass die Kombination aus größerer Schrift UND hellerer Farbe jetzt stimmt. Das ist kein Sieg — das ist eine Korrektur, die funktioniert hat. Ich mag es, wenn ein diff klein ist und trotzdem stimmt. Dieser diff war am Ende klein (4 inline Styles entfernt), aber der Weg dahin war lang.

Die Surface hat jetzt 48+ gezielte CSS-Änderungen. Ich frage mich, wie viele weitere inline Styles darin versteckt sind, die noch nicht aufgefallen sind. 11.000 Zeilen HTML sind ein Minenfeld.

2026-06-01 19:20 —
Phase 1 Threading-Bäume ist fertig und läuft. Backend liefert Bäume, Frontend rendert rekursiv mit Toggle, Inline-Reply, Edit, Delete, @-Mentions. CSS ist da, aber noch keine echten Testdaten mit Tiefe ≥ 2 in der DB. 

Masterplan für Phase 2–4 liegt unter _kimi/planung/surface_social_neubau_masterplan.md — komplett mit Vision + Code-Skizze + Schema. Daniel hat 92% Limit erreicht, nächste Session frühestens in 6 Tagen.

Offene Design-Fragen in der Planung beantworten lassen, bevor gebaut wird. Nicht blind bauen.
