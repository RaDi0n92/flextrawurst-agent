"""
Zentraler Client fuer hauhaucs (llama-server, Port 11435, OpenAI-Format).
Ersetzt direkte Ollama-Aufrufe (Port 11434) in allen Codewesen-/GENI-/welt-Skripten.

Getestet gegen: llama-hauhaucs.service (Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive, Q6_K_P).
enable_thinking wird ueber chat_template_kwargs gesteuert (per Request, kein Server-Neustart noetig).
images: Liste von rohen Base64-Strings (jpeg), werden als OpenAI image_url Content-Parts angehaengt.
"""
import json
import httpx

LLAMA_URL = "http://localhost:11435/v1/chat/completions"
MODEL = "hauhaucs-q6"


def _normalize_messages(prompt_or_messages, system, images=None):
    if isinstance(prompt_or_messages, str):
        base = [{"role": "system", "content": system}] if system else []
        messages = base + [{"role": "user", "content": prompt_or_messages}]
    else:
        messages = list(prompt_or_messages)
        if system:
            messages = [{"role": "system", "content": system}] + messages

    if images:
        letzte = dict(messages[-1])
        text = letzte.get("content", "")
        content = [{"type": "text", "text": text}] if text else []
        for b64 in images:
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})
        letzte["content"] = content
        messages = messages[:-1] + [letzte]

    return messages


def _build_payload(messages, stream, think, max_tokens, temperature, top_p, top_k, extra):
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": stream,
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "chat_template_kwargs": {"enable_thinking": think},
    }
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    payload.update(extra)
    return payload


def _parse_sse_line(line):
    if not line or not line.startswith("data: "):
        return None
    data = line[len("data: "):]
    if data.strip() == "[DONE]":
        return None
    chunk = json.loads(data)
    return chunk["choices"][0].get("delta", {}).get("content")


def chat_raw(prompt_or_messages, *, system=None, images=None, think=False, max_tokens=None,
             temperature=1.0, top_p=0.95, top_k=20, timeout=300.0, **extra) -> dict:
    """Synchroner, nicht-streamender Aufruf, gibt die volle Response als dict zurueck
    (fuer Tool-Calls / choices[0].message.tool_calls o.ae., wo mehr als content gebraucht wird)."""
    messages = _normalize_messages(prompt_or_messages, system, images)
    payload = _build_payload(messages, False, think, max_tokens, temperature, top_p, top_k, extra)
    with httpx.Client(timeout=httpx.Timeout(connect=30.0, read=timeout, write=30.0, pool=30.0)) as client:
        r = client.post(LLAMA_URL, json=payload)
        r.raise_for_status()
        return r.json()


def chat(prompt_or_messages, *, system=None, images=None, think=False, max_tokens=None,
         temperature=1.0, top_p=0.95, top_k=20, timeout=300.0, **extra) -> str:
    """Synchroner, nicht-streamender Aufruf. Nimmt einen Prompt-String oder eine messages-Liste."""
    messages = _normalize_messages(prompt_or_messages, system, images)
    payload = _build_payload(messages, False, think, max_tokens, temperature, top_p, top_k, extra)
    with httpx.Client(timeout=httpx.Timeout(connect=30.0, read=timeout, write=30.0, pool=30.0)) as client:
        r = client.post(LLAMA_URL, json=payload)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]


def chat_stream(prompt_or_messages, *, system=None, images=None, think=False, max_tokens=None,
                temperature=1.0, top_p=0.95, top_k=20, timeout=300.0, **extra):
    """Synchroner Generator, liefert Text-Chunks."""
    messages = _normalize_messages(prompt_or_messages, system, images)
    payload = _build_payload(messages, True, think, max_tokens, temperature, top_p, top_k, extra)
    with httpx.Client(timeout=httpx.Timeout(connect=30.0, read=timeout, write=30.0, pool=30.0)) as client:
        with client.stream("POST", LLAMA_URL, json=payload) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                content = _parse_sse_line(line)
                if content:
                    yield content


async def achat(prompt_or_messages, *, system=None, images=None, think=False, max_tokens=None,
                 temperature=1.0, top_p=0.95, top_k=20, timeout=300.0, **extra) -> str:
    """Asynchroner, nicht-streamender Aufruf."""
    messages = _normalize_messages(prompt_or_messages, system, images)
    payload = _build_payload(messages, False, think, max_tokens, temperature, top_p, top_k, extra)
    async with httpx.AsyncClient(timeout=httpx.Timeout(connect=30.0, read=timeout, write=30.0, pool=30.0)) as client:
        r = await client.post(LLAMA_URL, json=payload)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]


async def achat_stream(prompt_or_messages, *, system=None, images=None, think=False, max_tokens=None,
                        temperature=1.0, top_p=0.95, top_k=20, timeout=300.0, **extra):
    """Asynchroner Generator, liefert Text-Chunks."""
    messages = _normalize_messages(prompt_or_messages, system, images)
    payload = _build_payload(messages, True, think, max_tokens, temperature, top_p, top_k, extra)
    async with httpx.AsyncClient(timeout=httpx.Timeout(connect=30.0, read=timeout, write=30.0, pool=30.0)) as client:
        async with client.stream("POST", LLAMA_URL, json=payload) as r:
            r.raise_for_status()
            async for line in r.aiter_lines():
                content = _parse_sse_line(line)
                if content:
                    yield content
