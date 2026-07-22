import asyncio
from playwright.async_api import async_playwright
import os

BASE = "http://localhost:8787/flextrawurst_surface.html"
OUT = "/root/werkraum/_kimi/inventur/screenshots"

TABS = [
    ("leitstand", "LEITSTAND"),
    ("uber", "WAS IST DAS?"),
    ("weltstrom", "WELTSTROM"),
    ("raume", "RÄUME"),
    ("diskurs", "DISKURS"),
    ("wesen", "WESEN"),
    ("denken", "DENKEN"),
    ("screens", "SCREENS"),
    ("theater", "KOMPOASE"),
    ("blasen", "BLASEN"),
    ("menschen", "MENSCHEN"),
    ("schlaf", "SCHLAF"),
    ("einsicht", "EINSICHT"),
    ("suche", "SUCHE"),
    ("archaeologie", "ARCHÄOLOGIE"),
    ("cyberlinge", "CYBERLINGE"),
    ("splitter", "SPLITTER"),
    ("zitate", "ZITATE"),
    ("schatten", "SCHATTEN"),
    ("gruppen", "GRUPPEN"),
    ("systeme", "SYSTEME"),
    ("wissen", "WISSEN"),
    ("gesetze", "GESETZE"),
    ("forschung", "FORSCHUNG"),
    ("partner", "PARTNER"),
]

HIDDEN = [("meinewelt", "MEINE WELT"), ("admin", "ADMIN"), ("gordslider", "GORDSLIDER")]

async def switch_to(page, view, label):
    await page.goto(BASE)
    await page.wait_for_timeout(800)
    # dismiss splash
    splash = await page.query_selector("#splash")
    if splash and await splash.is_visible():
        await splash.click()
        await page.wait_for_timeout(800)
    # click tab by text
    btn = await page.query_selector(f'.v-tab[data-view="{view}"]')
    if btn:
        await btn.click()
        await page.wait_for_timeout(1200)
    else:
        # fallback: try js switch
        await page.evaluate(f"switchView('{view}')")
        await page.wait_for_timeout(1200)

async def screenshot_tab(page, view, label):
    await switch_to(page, view, label)
    name = f"tab_{view}"
    path = os.path.join(OUT, f"{name}.png")
    await page.screenshot(path=path, full_page=True)
    print(f"Saved {path}")

async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1600, "height": 1000})
        for view, label in TABS:
            await screenshot_tab(page, view, label)
        for view, label in HIDDEN:
            await switch_to(page, view, label)
            # make visible via JS for screenshot
            await page.evaluate(f'''
                const t=document.querySelector('.v-tab[data-view="{view}"]');
                if(t)t.style.display='inline-flex';
                const v=document.getElementById('v-{view}');
                if(v){{v.style.display='flex'; v.style.flexDirection='column';}}
            ''')
            await page.wait_for_timeout(800)
            path = os.path.join(OUT, f"tab_hidden_{view}.png")
            await page.screenshot(path=path, full_page=True)
            print(f"Saved {path}")
        await browser.close()

asyncio.run(main())
