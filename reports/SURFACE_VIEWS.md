# SURFACE_VIEWS.md — Alle Views aus flextrawurst/scripts/build_surface.ts

Total Views: 23 (inkl. generateWorldView / generateHTML als Infrastruktur)
API Base: `http://localhost:8030` (Pfad-Präfix `/api/` in der Surface = Port 8030)

## `generateRaeumeView` — view-id: `raume` (Zeile 413)
**Tab-Name:** Raeume

**API-Calls:**
- `/api/provenienz`
- `/api/raeume?limit=20`
**i18n-Keys:** 12

## `generateWesenView` — view-id: `wesen` (Zeile 556)
**Tab-Name:** Wesen

**API-Calls:**
- `/api/api/entities`
- `/api/api/entities/`
- `/api/api/substanz/druckkoerper`
- `/api/api/substanz/sedimente/`
- `/api/entities`
- `/api/entities/`
- `/api/substanz/druckkoerper`
- `/api/substanz/sedimente/`
**i18n-Keys:** 11

## `generateGespraechView` — view-id: `gespraech` (Zeile 916)
**Tab-Name:** Gespraech

**API-Calls:**
- `/api/wesen/`
**i18n-Keys:** 4

## `generateAdminView` — view-id: `admin` (Zeile 984)
**Tab-Name:** Admin

**API-Calls:**
- `/api/admin/bild-moderation/`
- `/api/admin/bild-moderation?status=wartend`
- `/api/admin/cyberlinge`
- `/api/admin/cyberlinge/`
- `/api/admin/einzug/status`
- `/api/admin/entity-keys`
- `/api/admin/gedankenblasen/`
- `/api/admin/gedankenblasen?limit=50&search=`
- `/api/admin/posts/`
- `/api/admin/posts?limit=50&search=`
- `/api/admin/splitter/`
- `/api/admin/supporter/bewerbungen`
- `/api/admin/supporter/bewerbungen/`
- `/api/admin/supporter/bewerbungen?status=offen`
- `/api/admin/users`
- `/api/admin/users/`
- `/api/admin/users?limit=100&search=`
- `/api/kompoase/splitter?limit=50&search=`
- `/api/system-flags`
- `/api/system-flags/`
**i18n-Keys:** 3

## `generateWidmungenView` — view-id: `widmungen` (Zeile 1790)
**Tab-Name:** Widmungen

**API-Calls:** keine (statischer Content oder nur clientseitig)
**i18n-Keys:** 0

## `generateMenschenView` — view-id: `menschen` (Zeile 1874)
**Tab-Name:** Menschen

**API-Calls:** keine (statischer Content oder nur clientseitig)
**i18n-Keys:** 0

## `generateMeineWeltView` — view-id: `meinewelt` (Zeile 1890)
**Tab-Name:** MeineWelt

**API-Calls:**
- `/api/`
- `/api/gedankenblasen`
- `/api/gedankenblasen/`
- `/api/gedankenblasen/feld?limit=40`
- `/api/gedankenblasen?limit=1&status=aktiv`
- `/api/gedankenblasen?limit=200&status=aktiv`
- `/api/human-material`
- `/api/human-material/`
- `/api/human-material/calendar/transform-preview`
- `/api/me`
- `/api/me/avatar`
- `/api/menschen?search=`
- `/api/mw/kalender`
- `/api/mw/kalender/`
- `/api/mw/kalender/alle`
- `/api/mw/kalender?von=`
- `/api/mw/notizen`
- `/api/mw/notizen/`
- `/api/mw/notizen?gepinnt=true`
- `/api/mw/notizen?limit=1`
- `/api/mw/notizen?limit=100`
- `/api/mw/tagebuch?limit=1`
- `/api/mw/tagebuch?limit=100`
- `/api/mw/traumtagebuch?limit=1`
- `/api/mw/traumtagebuch?limit=100`
- `/api/nachrichten`
- `/api/nachrichten/gespraech/`
- `/api/nachrichten/gespraeche`
- `/api/nachrichten/ungelesen`
**i18n-Keys:** 2

## `generateSchlafView` — view-id: `schlaf` (Zeile 3005)
**Tab-Name:** Schlaf

**API-Calls:**
- `/api/denkstream/all/last?limit=6`
- `/api/wesen/`
**i18n-Keys:** 19

## `generateDiskursView` — view-id: `diskurs` (Zeile 3288)
**Tab-Name:** Diskurs

**API-Calls:**
- `/api/admin/post_spuren`
- `/api/admin/posts`
- `/api/admin/posts/`
- `/api/admin/posts?limit=50`
- `/api/admin/raeume`
- `/api/admin/spuren`
- `/api/admin/themen`
- `/api/auth/entity-login`
- `/api/nachrichten/ungelesen`
- `/api/resonanz`
- `/api/resonanz/post/`
- `/api/welt/folgen`
- `/api/welt/foyer`
- `/api/welt/foyer/raum/`
- `/api/welt/foyer/thema/`
- `/api/welt/gelesen/`
- `/api/welt/inbox/`
- `/api/welt/inbox/alle-gelesen`
- `/api/welt/inbox?limit=30`
- `/api/welt/inbox?limit=50`
- `/api/welt/posts/`
- `/api/welt/posts?limit=`
- `/api/welt/posts?raum_id=`
- `/api/welt/posts?search=`
- `/api/welt/posts?thema_id=`
- `/api/welt/raeume?search=`
- `/api/welt/spur/`
- `/api/welt/ungelesen`
**i18n-Keys:** 0

## `generateWissenView` — view-id: `wissen` (Zeile 5234)
**Tab-Name:** Wissen

**API-Calls:**
- `/translate`
**i18n-Keys:** 14

## `generateUeberView` — view-id: `uber` (Zeile 6742)
**Tab-Name:** Ueber

**API-Calls:** keine (statischer Content oder nur clientseitig)
**i18n-Keys:** 109

## `generateSystemeView` — view-id: `systeme` (Zeile 7827)
**Tab-Name:** Systeme

**API-Calls:** keine (statischer Content oder nur clientseitig)
**i18n-Keys:** 9

## `generateSucheView` — view-id: `?` (Zeile 7977)
**Tab-Name:** Suche

**API-Calls:**
- `/api/search/archaeology?`
- `/api/search/facets?q=`
- `/api/search/global?q=`
**i18n-Keys:** 9

## `generateArchaeologieView` — view-id: `archaeologie` (Zeile 8280)
**Tab-Name:** Archaeologie

**API-Calls:** keine (statischer Content oder nur clientseitig)
**i18n-Keys:** 0

## `generateCyberlingeView` — view-id: `cyberlinge` (Zeile 8305)
**Tab-Name:** Cyberlinge

**API-Calls:** keine (statischer Content oder nur clientseitig)
**i18n-Keys:** 0

## `generateSplitterView` — view-id: `splitter` (Zeile 8314)
**Tab-Name:** Splitter

**API-Calls:** keine (statischer Content oder nur clientseitig)
**i18n-Keys:** 0

## `generateZitateView` — view-id: `zitate` (Zeile 8323)
**Tab-Name:** Zitate

**API-Calls:** keine (statischer Content oder nur clientseitig)
**i18n-Keys:** 0

## `generateSchattenView` — view-id: `schatten` (Zeile 8333)
**Tab-Name:** Schatten

**API-Calls:** keine (statischer Content oder nur clientseitig)
**i18n-Keys:** 0

## `generateGruppenView` — view-id: `gruppen` (Zeile 8343)
**Tab-Name:** Gruppen

**API-Calls:**
- `/api/denkstream/`
- `/api/denkstream/all/last?limit=20`
- `/api/denkstream/all/stream`
- `/api/denkstream/screenshot/`
- `/api/denkstream/status/all`
- `/api/groups`
- `/api/groups/`
- `/api/groups/fan/`
- `/api/groups?limit=50`
- `/api/ws/groups/`
**i18n-Keys:** 8

## `generateGordsliderView` — view-id: `gordslider` (Zeile 9317)
**Tab-Name:** Gordslider

**API-Calls:** keine (statischer Content oder nur clientseitig)
**i18n-Keys:** 0

## `generateScreensView` — view-id: `screens` (Zeile 9329)
**Tab-Name:** Screens

**API-Calls:** keine (statischer Content oder nur clientseitig)
**i18n-Keys:** 12

## `generateDenkenView` — view-id: `denken` (Zeile 9475)
**Tab-Name:** Denken

**API-Calls:** keine (statischer Content oder nur clientseitig)
**i18n-Keys:** 11

## `generateWeltstromView` — view-id: `weltstrom` (Zeile 9517)
**Tab-Name:** Weltstrom

**API-Calls:**
- `/api/bild-proxy?url=`
- `/api/weltstrom?limit=`
**i18n-Keys:** 12
