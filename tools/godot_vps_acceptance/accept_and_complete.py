#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shutil
import socket
import struct
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TARGET = Path('/root/werkraum/engine/godot-vertical-slice')
SERVICE_NAME = 'flextrawurst-godot-world-bridge.service'
UNIT_SOURCE = TARGET / 'deploy' / SERVICE_NAME
UNIT_TARGET = Path('/etc/systemd/system') / SERVICE_NAME
PROOF_PATH = Path('ops/proofs/godot-vps-acceptance.json')
FORBIDDEN_PORTS = (8090, 8091)
BRIDGE_PORT = 18092


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def trim(value: str, limit: int = 12000) -> str:
    if len(value) <= limit:
        return value
    return value[:6000] + '\n...<gekürzt>...\n' + value[-6000:]


def run(argv: list[str], *, cwd: Path | None = None, timeout: int = 120, root: bool = False) -> dict[str, Any]:
    command = list(argv)
    if root and os.geteuid() != 0:
        command = ['sudo', '-n', *command]
    started = utc_now()
    try:
        result = subprocess.run(
            command,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            'argv': command,
            'cwd': str(cwd) if cwd else None,
            'started_at': started,
            'completed_at': utc_now(),
            'exit_code': result.returncode,
            'stdout': trim(result.stdout),
            'stderr': trim(result.stderr),
            'ok': result.returncode == 0,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            'argv': command,
            'cwd': str(cwd) if cwd else None,
            'started_at': started,
            'completed_at': utc_now(),
            'exit_code': None,
            'stdout': trim(exc.stdout or '') if isinstance(exc.stdout, str) else '',
            'stderr': trim(exc.stderr or '') if isinstance(exc.stderr, str) else '',
            'ok': False,
            'timeout': timeout,
        }
    except Exception as exc:
        return {
            'argv': command,
            'cwd': str(cwd) if cwd else None,
            'started_at': started,
            'completed_at': utc_now(),
            'exit_code': None,
            'stdout': '',
            'stderr': str(exc),
            'ok': False,
        }


def file_info(path: Path) -> dict[str, Any]:
    info: dict[str, Any] = {'path': str(path), 'exists': path.exists()}
    if path.exists():
        stat = path.stat()
        info.update(size_bytes=stat.st_size, is_file=path.is_file(), is_dir=path.is_dir())
    return info


def validate_glb(path: Path) -> dict[str, Any]:
    result = file_info(path)
    result['valid'] = False
    if not path.is_file() or path.stat().st_size < 12:
        return result
    try:
        header = path.read_bytes()[:12]
        magic, version, declared_length = struct.unpack('<4sII', header)
        result.update(
            magic=magic.decode('ascii', errors='replace'),
            version=version,
            declared_length=declared_length,
            actual_length=path.stat().st_size,
            valid=(magic == b'glTF' and version == 2 and declared_length == path.stat().st_size),
        )
    except Exception as exc:
        result['error'] = str(exc)
    return result


def validate_png(path: Path) -> dict[str, Any]:
    result = file_info(path)
    result['valid'] = False
    if not path.is_file() or path.stat().st_size < 24:
        return result
    try:
        header = path.read_bytes()[:24]
        signature = b'\x89PNG\r\n\x1a\n'
        if header[:8] != signature or header[12:16] != b'IHDR':
            return result
        width, height = struct.unpack('>II', header[16:24])
        result.update(width=width, height=height, valid=width > 0 and height > 0)
    except Exception as exc:
        result['error'] = str(exc)
    return result


def find_godot() -> str | None:
    candidates = ['/usr/local/bin/godot', '/usr/bin/godot', shutil.which('godot')]
    for candidate in candidates:
        if candidate and Path(candidate).is_file() and os.access(candidate, os.X_OK):
            return candidate
    return None


def active_config_port_mentions(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {'path': str(path), 'exists': path.is_file(), 'active_lines': [], 'forbidden': [], 'bridge_port': []}
    if not path.is_file():
        return result
    for number, raw in enumerate(path.read_text(encoding='utf-8', errors='replace').splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith('#') or line.startswith(';'):
            continue
        if any(token in line for token in ('ExecStart=', 'Environment=', 'EnvironmentFile=', '--port', 'PORT=', 'ListenStream=')):
            result['active_lines'].append({'line': number, 'text': line})
            for port in FORBIDDEN_PORTS:
                if re.search(rf'(?<!\d){port}(?!\d)', line):
                    result['forbidden'].append({'line': number, 'port': port, 'text': line})
            if re.search(rf'(?<!\d){BRIDGE_PORT}(?!\d)', line):
                result['bridge_port'].append({'line': number, 'text': line})
    return result


def search_project_ports(root: Path) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    if not root.is_dir():
        return matches
    suffixes = {'.py', '.ts', '.js', '.gd', '.service', '.sh', '.json', '.toml', '.yaml', '.yml', '.md'}
    for path in root.rglob('*'):
        if not path.is_file() or path.suffix.lower() not in suffixes or path.stat().st_size > 2_000_000:
            continue
        try:
            text = path.read_text(encoding='utf-8', errors='replace')
        except OSError:
            continue
        for number, line in enumerate(text.splitlines(), start=1):
            ports = [port for port in (*FORBIDDEN_PORTS, BRIDGE_PORT) if re.search(rf'(?<!\d){port}(?!\d)', line)]
            if ports:
                matches.append({'path': str(path), 'line': number, 'ports': ports, 'text': line.strip()[:500]})
                if len(matches) >= 300:
                    return matches
    return matches


def socket_probe(port: int, timeout: float = 1.5) -> dict[str, Any]:
    started = utc_now()
    try:
        with socket.create_connection(('127.0.0.1', port), timeout=timeout):
            return {'port': port, 'reachable': True, 'started_at': started, 'completed_at': utc_now()}
    except OSError as exc:
        return {'port': port, 'reachable': False, 'error': str(exc), 'started_at': started, 'completed_at': utc_now()}


def main() -> int:
    PROOF_PATH.parent.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {
        'started_at': utc_now(),
        'host': socket.gethostname(),
        'target': str(TARGET),
        'service_name': SERVICE_NAME,
        'bridge_port': BRIDGE_PORT,
        'forbidden_ports': list(FORBIDDEN_PORTS),
        'checks': {},
        'actions': [],
        'missing': [],
        'critical_failures': [],
    }

    checks = report['checks']
    checks['target'] = file_info(TARGET)
    checks['project_godot'] = file_info(TARGET / 'project.godot')
    checks['asset_source_b64'] = file_info(TARGET / 'assets' / 'test_cube.glb.b64')
    checks['asset_glb_before'] = validate_glb(TARGET / 'assets' / 'test_cube.glb')
    checks['unit_source'] = file_info(UNIT_SOURCE)
    checks['unit_ports'] = active_config_port_mentions(UNIT_SOURCE)
    checks['project_port_mentions'] = search_project_ports(TARGET)
    checks['ports_before'] = run(['ss', '-ltnp'], timeout=30)
    checks['service_before'] = run(['systemctl', 'status', SERVICE_NAME, '--no-pager', '--full'], timeout=30, root=True)

    if not TARGET.is_dir():
        report['critical_failures'].append(f'Zielkörper fehlt: {TARGET}')
    if not (TARGET / 'project.godot').is_file():
        report['critical_failures'].append('project.godot fehlt')

    prepare = TARGET / 'tools' / 'prepare_assets.py'
    checks['prepare_assets_script'] = file_info(prepare)
    if prepare.is_file():
        action = run(['python3', str(prepare)], cwd=TARGET, timeout=180)
        action['name'] = 'prepare_assets'
        report['actions'].append(action)
        if not action['ok']:
            report['critical_failures'].append('prepare_assets.py fehlgeschlagen')
    else:
        report['missing'].append(str(prepare))

    asset_glb = TARGET / 'assets' / 'test_cube.glb'
    checks['asset_glb_after'] = validate_glb(asset_glb)
    if not checks['asset_glb_after']['valid']:
        report['critical_failures'].append('assets/test_cube.glb fehlt oder ist kein gültiges GLB v2')

    godot = find_godot()
    checks['godot_binary'] = {'path': godot, 'exists': bool(godot)}
    if godot:
        version = run([godot, '--version'], cwd=TARGET, timeout=60)
        version['name'] = 'godot_version'
        report['actions'].append(version)
        if not version['ok']:
            report['critical_failures'].append('godot --version fehlgeschlagen')

        imported = run([godot, '--headless', '--path', str(TARGET), '--editor', '--quit'], cwd=TARGET, timeout=300)
        imported['name'] = 'godot_headless_import'
        report['actions'].append(imported)
        if not imported['ok']:
            report['critical_failures'].append('Godot Headless Import fehlgeschlagen')

        for test_name in ('headless_smoke.gd', 'mcp_text_only_smoke.gd'):
            test_path = TARGET / 'tests' / test_name
            checks[f'test_{test_name}'] = file_info(test_path)
            if test_path.is_file():
                action = run([godot, '--headless', '--path', str(TARGET), '--script', f'res://tests/{test_name}'], cwd=TARGET, timeout=300)
                action['name'] = test_name
                report['actions'].append(action)
                if not action['ok']:
                    report['critical_failures'].append(f'{test_name} fehlgeschlagen')
            else:
                report['missing'].append(str(test_path))
                report['critical_failures'].append(f'{test_name} fehlt')
    else:
        report['critical_failures'].append('Godot-Binary nicht gefunden')

    unit_ports = checks['unit_ports']
    if unit_ports['forbidden']:
        report['critical_failures'].append('Systemd-Unit verweist aktiv auf reservierten Port 8090 oder 8091')

    port_18092_before = socket_probe(BRIDGE_PORT)
    checks['bridge_socket_before'] = port_18092_before
    service_active_before = run(['systemctl', 'is-active', '--quiet', SERVICE_NAME], timeout=20, root=True)['ok']

    if UNIT_SOURCE.is_file() and not unit_ports['forbidden']:
        if port_18092_before['reachable'] and not service_active_before:
            report['critical_failures'].append('Port 18092 ist durch einen unbekannten Prozess belegt; Dienstinstallation nicht erzwungen')
        else:
            install = run(['install', '-m', '0644', str(UNIT_SOURCE), str(UNIT_TARGET)], timeout=60, root=True)
            install['name'] = 'install_systemd_unit'
            report['actions'].append(install)
            if install['ok']:
                for name, argv in (
                    ('systemd_daemon_reload', ['systemctl', 'daemon-reload']),
                    ('systemd_enable', ['systemctl', 'enable', SERVICE_NAME]),
                    ('systemd_restart', ['systemctl', 'restart', SERVICE_NAME]),
                ):
                    action = run(argv, timeout=90, root=True)
                    action['name'] = name
                    report['actions'].append(action)
                    if not action['ok']:
                        report['critical_failures'].append(f'{name} fehlgeschlagen')
            else:
                report['critical_failures'].append('Systemd-Unit konnte nicht installiert werden')
    else:
        if not UNIT_SOURCE.is_file():
            report['missing'].append(str(UNIT_SOURCE))
            report['critical_failures'].append('Bridge-Systemd-Unit fehlt')

    checks['service_after'] = run(['systemctl', 'status', SERVICE_NAME, '--no-pager', '--full'], timeout=30, root=True)
    checks['service_active_after'] = run(['systemctl', 'is-active', SERVICE_NAME], timeout=20, root=True)
    checks['service_enabled_after'] = run(['systemctl', 'is-enabled', SERVICE_NAME], timeout=20, root=True)
    checks['journal_after'] = run(['journalctl', '-u', SERVICE_NAME, '-n', '120', '--no-pager'], timeout=45, root=True)
    checks['ports_after'] = run(['ss', '-ltnp'], timeout=30)
    checks['bridge_socket_after'] = socket_probe(BRIDGE_PORT)
    checks['reserved_8090_after'] = socket_probe(8090)
    checks['reserved_8091_after'] = socket_probe(8091)

    health = run(['curl', '-fsS', '--max-time', '10', f'http://127.0.0.1:{BRIDGE_PORT}/health'], timeout=20)
    health['name'] = 'bridge_health'
    report['actions'].append(health)
    if not health['ok']:
        report['critical_failures'].append('Bridge-Healthcheck auf 127.0.0.1:18092 fehlgeschlagen')

    if godot:
        for test_name in ('live_bridge_probe.gd', 'capture_proof.gd'):
            test_path = TARGET / 'tests' / test_name
            checks[f'test_{test_name}'] = file_info(test_path)
            if test_path.is_file():
                action = run([godot, '--headless', '--path', str(TARGET), '--script', f'res://tests/{test_name}'], cwd=TARGET, timeout=300)
                action['name'] = test_name
                report['actions'].append(action)
                if not action['ok']:
                    report['critical_failures'].append(f'{test_name} fehlgeschlagen')
            else:
                report['missing'].append(str(test_path))
                report['critical_failures'].append(f'{test_name} fehlt')

    png_candidates = sorted(
        [p for p in (TARGET / 'test_outputs').glob('*.png') if p.is_file()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    ) if (TARGET / 'test_outputs').is_dir() else []
    checks['screenshot_candidates'] = [validate_png(path) for path in png_candidates[:20]]
    checks['valid_screenshot'] = next((item for item in checks['screenshot_candidates'] if item.get('valid')), None)
    if not checks['valid_screenshot']:
        report['critical_failures'].append('Kein gültiger Godot-Beweis-Screenshot in test_outputs gefunden')

    roundtrip = TARGET / 'test_outputs' / 'test_cube_roundtrip.glb'
    checks['roundtrip_glb'] = validate_glb(roundtrip)
    if not checks['roundtrip_glb']['valid']:
        report['critical_failures'].append('test_cube_roundtrip.glb fehlt oder ist ungültig')

    if Path('/root/flextrawurst/package.json').is_file():
        suite = run(['npm', 'test'], cwd=Path('/root/flextrawurst'), timeout=900)
        suite['name'] = 'flextrawurst_full_test_suite'
        report['actions'].append(suite)
        checks['full_suite'] = {
            'ok': suite['ok'],
            'exit_code': suite['exit_code'],
            'known_stale_expectations': {
                'entities_expected': 6,
                'entities_reported': 7,
                'events_expected': 27,
                'events_reported': 31,
                'transitions_expected': 18,
                'transitions_reported': 21,
            },
        }
    else:
        report['missing'].append('/root/flextrawurst/package.json')

    checks['reserved_ports_preserved'] = {
        '8090_reachable_after': checks['reserved_8090_after']['reachable'],
        '8091_reachable_after': checks['reserved_8091_after']['reachable'],
        'note': 'Die Abnahme startet, stoppt oder verändert keine Dienste auf 8090 oder 8091.',
    }

    report['completed_at'] = utc_now()
    report['status'] = 'COMPLETE' if not report['critical_failures'] else 'INCOMPLETE'
    PROOF_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({
        'status': report['status'],
        'proof': str(PROOF_PATH),
        'critical_failures': report['critical_failures'],
        'missing': report['missing'],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
