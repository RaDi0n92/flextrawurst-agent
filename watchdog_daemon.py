import time, json, os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

LOG_PATH = "/tmp/werkraum_events.jsonl"
IGNORE_PREFIXES = ("watchdog/", ".obsidian/", ".trash/", "node_modules/", ".git/")
MAX_LINES = 300

class WerkraumHandler(FileSystemEventHandler):
    def _should_ignore(self, path):
        rel = path.replace("/root/werkraum/", "")
        return any(rel.startswith(p) for p in IGNORE_PREFIXES)

    def _log(self, event_type, path):
        if self._should_ignore(path):
            return
        entry = {"time": datetime.now().isoformat(), "type": event_type,
                 "path": path.replace("/root/werkraum/", "")}
        try:
            with open(LOG_PATH, "a") as f:
                f.write(json.dumps(entry) + "\n")
            # Trim nur alle 50 Events, nicht bei jedem
            if os.path.getsize(LOG_PATH) > 500000:
                with open(LOG_PATH, "r") as f:
                    lines = f.readlines()
                if len(lines) > MAX_LINES:
                    with open(LOG_PATH, "w") as f:
                        f.writelines(lines[-MAX_LINES:])
        except:
            pass

    def on_created(self, event):
        if not event.is_directory: self._log("created", event.src_path)
    def on_modified(self, event):
        if not event.is_directory: self._log("modified", event.src_path)
    def on_deleted(self, event):
        self._log("deleted", event.src_path)

if __name__ == "__main__":
    observer = Observer()
    observer.schedule(WerkraumHandler(), "/root/werkraum/", recursive=True)
    observer.start()
    print("Watchdog laeuft (log: /tmp/werkraum_events.jsonl)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
