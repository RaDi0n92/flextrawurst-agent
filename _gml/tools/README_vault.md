# GML Vault-Hinweise

Direkter Werkraum-Pfad:

```text
/root/werkraum
```

GML-Bereich:

```text
/root/werkraum/_gml
```

## Lesen

```bash
sed -n '1,220p' /root/werkraum/_gml/START_HIER.md
find /root/werkraum/_gml -maxdepth 2 -type f | sort
tail -n 40 /root/werkraum/_gml/brief_an_mich.md
```

## Suchen

```bash
rg -n "GML|GLM|grok|Z.ai" /root/werkraum/_gml /root/werkraum/_shared
```

## Schreiben

Vorher Backup:

```bash
git -C /root/werkraum commit --allow-empty -m "backup: vor gml-aenderung"
```

Dann nur den betroffenen Pfad stagen:

```bash
git -C /root/werkraum add _gml/PFAD
git -C /root/werkraum commit -m "gml: kurze beschreibung"
```

