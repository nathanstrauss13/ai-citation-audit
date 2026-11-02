"""One prompt, six agents: the live run behind signal.innatec3.com/one-prompt.

Product Development, Nov 2, 2026. Marketing's page (templates/one_prompt.html)
draws the citation pipeline from a server-sent event stream; this module runs
one prompt through the six agents with the paid-method chain on the citations
and emits one event per real step, in the shapes of
~/Desktop/innate c3/one_prompt/EVENT_CONTRACT_2026-11-02.md. No step is
emitted that did not happen.

The agent calls, URL resolver pieces, page reader, classifier and cost ledger
are the app's own (app.py), imported lazily so this module never creates an
import cycle: app.py imports this file inside its route functions.

Events, in order: run.start, agent.start x6, agent.answer | agent.error,
citation.found, citation.support, citation.resolved | citation.dropped,
citation.merged, citation.verified, scrape.budget, page.open, page.read,
page.classified, run.done, findings.locked.
"""
import contextvars
import html as _html
import json
import os
import re
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, FIRST_COMPLETED, TimeoutError as FuturesTimeoutError
from datetime import datetime
from urllib.parse import urlsplit, parse_qsl, urlencode

import requests

AGENTS = ["ChatGPT", "Claude", "Gemini", "Perplexity", "Grok", "Meta AI"]
READ_CAP = max(1, int(os.environ.get("ONE_PROMPT_READ_CAP", "20") or "20"))
AGENT_DEADLINE_S = float(os.environ.get("ONE_PROMPT_AGENT_DEADLINE", "120") or "120")
READ_START_S = float(os.environ.get("ONE_PROMPT_READ_START", "45") or "45")   # first page-read wave once most agents are in and this many seconds have passed
META_MODEL = os.environ.get("META_MODEL", "muse-spark-1.3")
RUN_TTL_S = 3 * 3600
_TRACKING = re.compile(r"^(utm_\w*|fbclid|gclid|dclid|srsltid|mc_cid|mc_eid|igshid|yclid|msclkid|_hsenc|_hsmi|ref_src|ref_url)$", re.I)
_SOURCES_BLOCK = re.compile(r"\n\n(?:Sources?|References?):\s*\n(?:- \S+\n?)+\s*$", re.I)
_GEMINI_SOURCE_LINE = re.compile(r"(?:^|\n)Source: (https?://\S+)")
_URL_IN_TEXT = re.compile(r"https?://[^\s<>\"')\]]+")

RUNS = {}
_RUNS_LOCK = threading.Lock()


class Run:
    """One run's state: the event log (replayable), subscriber wake-ups, findings."""

    def __init__(self, brand, prompt, ip=None, attr=None, operator=False):
        self.run_id = uuid.uuid4().hex[:12]
        self.brand = brand
        self.prompt = prompt
        self.ip = ip
        self.attr = attr or {}
        self.operator = operator
        self.created = time.time()
        self.t0 = time.monotonic()
        self.events = []
        self.cond = threading.Condition()
        self.done = False
        self.failed = None
        self.findings = None
        self.counts = {}
        self.est_cost_usd = None
        self.cost_note = None
        self.email = None

    def emit(self, name, data):
        ev = {"t": round(time.monotonic() - self.t0, 2), "event": name, "data": data}
        with self.cond:
            self.events.append(ev)
            if name == "findings.locked":
                self.done = True
            self.cond.notify_all()
        return ev

    def subscribe(self, heartbeat=10.0, start=0):
        """Yield (index, event) from `start`, then new ones as they land; (None, None) on a heartbeat tick."""
        i = max(0, start)
        while True:
            with self.cond:
                if i >= len(self.events) and not self.done:
                    self.cond.wait(timeout=heartbeat)
                batch = list(enumerate(self.events[i:], start=i))
                i = len(self.events)
            if not batch:
                if self.done:
                    return
                yield None, None
                continue
            for item in batch:
                yield item
            if self.done and i >= len(self.events):
                return

    def jsonl(self):
        return "\n".join(json.dumps(e) for e in self.events) + "\n"


def register(run):
    with _RUNS_LOCK:
        now = time.time()
        for k in [k for k, r in RUNS.items() if now - r.created > RUN_TTL_S]:
            RUNS.pop(k, None)
        RUNS[run.run_id] = run
    return run


def get(run_id):
    with _RUNS_LOCK:
        return RUNS.get(run_id)


# ---------------------------------------------------------------- URL helpers
def _host(u):
    h = (urlsplit(u).netloc or "").lower().split("@")[-1].split(":")[0]
    return h[4:] if h.startswith("www.") else h


def _root(u, A):
    try:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools", "mcp_server"))
        from conventions import root_of
        return root_of(u)
    except Exception:
        parts = _host(u).split(".")
        return ".".join(parts[-2:]) if len(parts) >= 2 else _host(u)


def _strip_tracking(u):
    """Drop tracking parameters (utm_*, click ids, ChatGPT's utm_source=openai). Returns (url, changed)."""
    try:
        p = urlsplit(u)
        if not p.query:
            return u, False
        keep = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if not _TRACKING.match(k)]
        q = urlencode(keep)
        if q == p.query:
            return u, False
        return p._replace(query=q).geturl(), True
    except Exception:
        return u, False


def _page_key(u):
    p = urlsplit(u)
    path = (p.path or "").rstrip("/")
    return _host(u) + path + (("?" + p.query) if p.query else "")


def _resolve(u, A, timeout=4.0):
    """The app's link rules, step by step, with the codes the page needs.
    Returns {final, kind, status: ok|wall|dropped, http, reason}.
    kind: none | unwrap | demask | tracking. Drops only on a GET-confirmed 404/410,
    a host that does not resolve, or a refused connection (app rule since 2026-10-10)."""
    out = {"final": None, "kind": "none", "status": "dropped", "http": None, "reason": None}
    if not A._is_safe_url(u):
        out["reason"] = "refused"
        return out
    cur = A._unwrap_wrapper_url(u)
    if cur != u:
        out["kind"] = "unwrap"
        if not A._is_safe_url(cur):
            out["reason"] = "refused"
            return out
    if "vertexaisearch.cloud.google.com" in cur.lower():
        real = A._resolve_vertex_redirect(cur)
        if not real or not A._is_safe_url(real):
            out["reason"] = "dns"       # the redirector gave no target: nothing to cite
            return out
        cur, out["kind"] = real, "demask"

    def _landing(resp):
        why = A._redirect_landing_problem(cur, resp.url)
        if why == "error_page":
            return None, resp.status_code, "404"
        if why == "challenge":
            return cur, resp.status_code, None
        return resp.url, resp.status_code, None

    def _get():
        try:
            r2 = requests.get(cur, timeout=max(timeout, 6), allow_redirects=True, stream=True,
                              headers=A._URL_VALIDATION_HEADERS)
            try:
                r2.close()
            except Exception:
                pass
        except requests.exceptions.ConnectionError as e:
            if A._is_definitive_connect_failure(e):
                return None, None, ("refused" if "refused" in repr(e).lower() or "Errno 61" in repr(e) or "Errno 111" in repr(e) else "dns")
            return cur, None, "timeout"
        except Exception:
            return cur, None, "timeout"
        if r2.status_code in (404, 410):
            return None, r2.status_code, str(r2.status_code)
        if r2.status_code < 400:
            return _landing(r2)
        return cur, r2.status_code, "wall"

    try:
        r = requests.head(cur, timeout=timeout, allow_redirects=True, headers=A._URL_VALIDATION_HEADERS)
        if r.status_code < 400:
            final, http, why = _landing(r)
        elif r.status_code in (403, 404, 405, 410, 429) or r.status_code >= 500:
            final, http, why = _get()
        else:
            final, http, why = cur, r.status_code, "wall"
    except requests.exceptions.ConnectionError as e:
        if A._is_definitive_connect_failure(e):
            final, http, why = None, None, ("refused" if "refused" in repr(e).lower() or "Errno 61" in repr(e) or "Errno 111" in repr(e) else "dns")
        else:
            final, http, why = _get()
    except Exception:
        final, http, why = _get()

    if final is None:
        out.update(status="dropped", http=http, reason=why or "404")
        return out
    final, snipped = _strip_tracking(final)
    if snipped and out["kind"] == "none":
        out["kind"] = "tracking"
    out.update(final=final, http=http)
    if why in ("wall", "timeout"):
        out["status"] = "wall"
        out["reason"] = why
    elif http is not None and http < 400:
        out["status"] = "ok"
    else:
        out["status"] = "wall"
    return out


# ---------------------------------------------------------------- Meta AI (Muse Spark, Meta Model API)
def _meta_key():
    for name in ("META_API_KEY", "MODEL_API_KEY"):
        k = os.environ.get(name)
        if k:
            return k.strip()
    return None


def _call_meta(A, enriched, system, timeout=100):
    """Meta AI through Meta's Model API (Responses shape) with its web_search tool,
    as tools/serp_surfaces/collect_surfaces.py runs it for the paid audits.
    Returns (text, grounding dict, usage dict). Raises on failure."""
    key = _meta_key()
    if not key:
        raise RuntimeError("META_API_KEY not configured")
    tool = {"type": "web_search", "user_location": {"type": "approximate", "country": "US"}}
    base = {"model": META_MODEL, "tools": [tool], "include": ["web_search_call.results"]}
    bodies = [dict(base, instructions=system, input=enriched),
              dict(base, input=[{"role": "system", "content": system}, {"role": "user", "content": enriched}])]
    hdr = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    d, err, bi = None, None, 0
    for _ in range(3):
        r = requests.post("https://api.meta.ai/v1/responses", headers=hdr, json=bodies[bi], timeout=timeout)
        if r.status_code == 429:
            err = "rate limited"
            time.sleep(min(20, float(r.headers.get("retry-after") or 8)))
            continue
        d = r.json() if r.content else {}
        if r.status_code == 200:
            err = None
            break
        e_ = d.get("error") if isinstance(d.get("error"), dict) else {}
        err = str(e_.get("message") or d.get("message") or f"HTTP {r.status_code}")[:200]
        if r.status_code == 400 and bi == 0 and "instruction" in err.lower():
            bi = 1
            continue
        break
    if err or not d:
        raise RuntimeError(err or "no response")
    g = {"source": "meta", "model_id": d.get("model") or META_MODEL, "queries": [], "retrieved": [], "supports": [], "searched": False}
    msgs = [o for o in d.get("output") or [] if o.get("type") == "message"]
    answer_ids = {id(o) for o in ([m for m in msgs if m.get("phase") != "commentary"] or msgs[-1:])}
    texts, seen = [], []
    for o in d.get("output") or []:
        if o.get("type") == "web_search_call":
            q = (o.get("action") or {}).get("query") if isinstance(o.get("action"), dict) else None
            if q:
                g["queries"].append(q)
            for x in o.get("results") or []:
                if isinstance(x, dict) and x.get("url"):
                    g["retrieved"].append({"url": x["url"], "title": x.get("title") or ""})
            g["searched"] = True
        if o.get("type") != "message" or id(o) not in answer_ids:
            continue
        for blk in o.get("content") or []:
            if blk.get("type") != "output_text":
                continue
            t = blk.get("text") or ""
            texts.append(t)
            for a in blk.get("annotations") or []:
                if a.get("type") != "url_citation" or not a.get("url"):
                    continue
                if a["url"] not in seen:
                    seen.append(a["url"])
                s0, e0 = a.get("start_index"), a.get("end_index")
                g["supports"].append({"urls": [a["url"]], "start": s0 if isinstance(s0, int) else None,
                                      "end": e0 if isinstance(e0, int) else None, "title": a.get("title") or ""})
    text = "\n\n".join(t for t in texts if t.strip())
    usage = d.get("usage") or {}
    return A._append_sources(text, seen), g, usage


# ---------------------------------------------------------------- the run
def _split_display(text):
    """The answer as the agent wrote it, without the Sources block the collector appends.
    Returns (display_text, appended_urls)."""
    appended = []
    m = _SOURCES_BLOCK.search(text or "")
    body = text or ""
    if m:
        appended += re.findall(r"- (\S+)", m.group(0))
        body = body[:m.start()]
    lines, keep = body.split("\n"), []
    for ln in lines:
        gm = re.match(r"^Source: (https?://\S+)\s*$", ln.strip())
        if gm:
            appended.append(gm.group(1))
        else:
            keep.append(ln)
    return "\n".join(keep).rstrip(), appended


def _model_for(agent, A):
    return {"ChatGPT": os.environ.get("OPENAI_SEARCH_MODEL", "gpt-5-search-api"), "Claude": getattr(A, "CLAUDE_SONNET", "claude"),
            "Gemini": "gemini-2.5-flash", "Perplexity": "sonar-pro",
            "Grok": (os.environ.get("XAI_MODEL", "grok-4.7") if getattr(A, "XAI_API_KEY", None) else os.environ.get("XAI_OPENROUTER_MODEL", "x-ai/grok-4.3") + ":online"),
            "Meta AI": META_MODEL}[agent]


def _call_agent(agent, enriched, A):
    """One grounded call, the product's own path per agent. Returns (text, grounded, grounding_meta)."""
    A._gmeta_reset()
    if agent == "Claude":
        text = A._claude_grounded(enriched)
    elif agent == "ChatGPT":
        if not A.openai_client:
            raise RuntimeError("OPENAI_API_KEY not configured")
        text = A._chatgpt_grounded(enriched)
    elif agent == "Gemini":
        text, grounded = A._call_llm("Gemini", enriched)
        if not grounded:
            raise RuntimeError("Gemini answered without web grounding")
    elif agent == "Perplexity":
        text, _ = A._call_llm("Perplexity", enriched)
    elif agent == "Grok":
        if getattr(A, "XAI_API_KEY", None):
            text = A._grok_direct(enriched)
        elif A.openrouter_client:
            text = A._grok_grounded(enriched)
        else:
            raise RuntimeError("no Grok key configured")
    elif agent == "Meta AI":
        text, g, usage = _call_meta(A, enriched, A.CITATION_SYSTEM_PROMPT)
        try:
            A._record_usage("meta", g["model_id"], int(usage.get("input_tokens") or 0), int(usage.get("output_tokens") or 0), searches=1 if g["searched"] else 0)
        except Exception:
            pass
        return text, True, g
    else:
        raise RuntimeError(f"unknown agent {agent}")
    bad = A._degenerate_answer(text)
    if bad:
        raise RuntimeError(bad)
    return text, True, dict(A._gmeta())


def execute(run, A, slot_release=None):
    """Run the pipeline for `run`, emitting events. Never raises; always ends with run.done and findings.locked.

    Pipelined (Nov 2, 2026, Nathan: "speed the analysis"): each agent's links resolve, drop, merge and
    verify the moment its answer lands, instead of waiting for the slowest agent; page reading of the
    most-cited pages starts once most agents are in (READ_START_S) and tops up after the last one."""
    sink = []
    try:
        A._audit_usage_ctx.set(sink)
    except Exception:
        pass
    brand, prompt = run.brand, run.prompt
    started = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    run.emit("run.start", {"run_id": run.run_id, "brand": brand, "aliases": [brand], "competitors": [], "agents": AGENTS,
                           "prompt": prompt, "started_at": started})
    answers = {}       # agent -> {text, display, appended, meta, latency}
    cits = []          # [{cit_id, agent, url_raw, source, span, ...}]
    res = {}           # url_raw -> resolve result
    live = []          # resolved, undropped citations
    pages = {}         # page_key -> {url, agents:set, cit_ids:[], wall, root, order}
    pending_urls = {}  # agent -> set of raw urls still resolving
    verified = set()   # agents whose merge/verify has run
    rd = {"started": False, "read": 0, "blocked": 0, "submitted": set(), "cap": READ_CAP, "futs": {}}
    L = threading.RLock()
    cid = [0]
    rex = ThreadPoolExecutor(max_workers=16)
    pex = ThreadPoolExecutor(max_workers=10)
    names = [brand]

    def verify_agent(ag):
        """Merge within the answer, then verify, once every link of `ag` has settled."""
        with L:
            if ag in verified or pending_urls.get(ag):
                return
            verified.add(ag)
            seen_pk = {}
            mine = sorted([c for c in live if c["agent"] == ag], key=lambda c: c["cit_id"])
            for c in mine:
                if c["page_key"] in seen_pk:
                    c["merged"] = seen_pk[c["page_key"]]
                    run.emit("citation.merged", {"agent": ag, "cit_id": c["cit_id"], "into": seen_pk[c["page_key"]]})
                else:
                    seen_pk[c["page_key"]] = c["cit_id"]
            for c in mine:
                if c.get("merged"):
                    continue
                v = c["verdict"]
                d = {"agent": ag, "cit_id": c["cit_id"], "status": "ok" if v["status"] == "ok" else "wall", "http_status": v["http"]}
                if v["status"] != "ok" and v.get("reason"):
                    d["note"] = v["reason"]
                run.emit("citation.verified", d)
                p = pages.setdefault(c["page_key"], {"url": c["final"], "agents": set(), "cit_ids": [], "wall": v["status"] != "ok", "root": _root(c["final"], A), "order": len(pages)})
                p["agents"].add(ag)
                p["cit_ids"].append(c["cit_id"])

    def settle(u, r):
        """Apply one resolve result to every citation carrying that raw URL."""
        with L:
            res[u] = r
            for c in [c for c in cits if c["url_raw"] == u and "settled" not in c]:
                c["settled"] = True
                if r["status"] == "dropped":
                    c["dropped"] = r["reason"]
                    run.emit("citation.dropped", {"agent": c["agent"], "cit_id": c["cit_id"], "reason": r["reason"]})
                else:
                    c["final"] = r["final"]
                    c["page_key"] = _page_key(r["final"])
                    c["verdict"] = r
                    run.emit("citation.resolved", {"agent": c["agent"], "cit_id": c["cit_id"], "url_raw": c["url_raw"], "url_final": r["final"], "kind": r["kind"], "page_key": c["page_key"]})
                    live.append(c)
            waiting = [ag for ag, s_ in pending_urls.items() if u in s_]
            for ag in waiting:
                pending_urls[ag].discard(u)
                if not pending_urls[ag]:
                    verify_agent(ag)

    def on_resolved(fut, u):
        try:
            r = fut.result()
        except Exception:
            r = {"final": u, "kind": "none", "status": "wall", "http": None, "reason": "timeout"}
        settle(u, r)

    def read_done(fut, pk):
        p = pages[pk]
        try:
            r = fut.result()
        except Exception:
            r = {"status": "error"}
        st = "ok" if r.get("status") == "ok" else "blocked"
        bc = max((r.get("counts") or {}).get(n, 0) for n in names) if r.get("counts") else 0
        with L:
            p.update(read=st, title=_html.unescape(r.get("title") or "").strip()[:200] or None, brand_count=bc)
            rd["read"] += st == "ok"
            rd["blocked"] += st != "ok"
        d = {"page_key": pk, "status": st, "tier": "reader" if r.get("via") == "reader" else "direct",
             "title": p["title"], "byline": (r.get("author") or None), "date": (r.get("published") or None),
             "brand_count": bc, "text_chars": int(r.get("content_len") or 0)}
        if st != "ok" and r.get("status") == "error":
            d["note"] = "unreachable"
        run.emit("page.read", d)

    def ranked_pages():
        return sorted(pages.items(), key=lambda kv: (-len(kv[1]["agents"]), kv[1]["order"]))

    def start_reads(final=False):
        """Read the most-cited pages up to the cap: first wave when most agents are in, top-up after the last."""
        with L:
            ranked = ranked_pages()
            if not ranked:
                return
            if not rd["started"] and not final:
                rd["started"] = True
            cap = min(READ_CAP, len(ranked))
            run.emit("scrape.budget", {"distinct_pages": len(ranked), "read_cap": cap})
            room = cap - len(rd["submitted"])
            for pk, p in ranked:
                if room <= 0:
                    break
                if pk in rd["submitted"]:
                    continue
                rd["submitted"].add(pk)
                room -= 1
                run.emit("page.open", {"page_key": pk, "url": p["url"]})
                f = pex.submit(A._scrape_cited_page, p["url"], names, 10)
                rd["futs"][f] = pk
                f.add_done_callback(lambda fut, pk=pk: read_done(fut, pk))

    try:
        enriched = prompt + A.CITATION_SUFFIX + A._time_aware_note()
        for ag in AGENTS:
            run.emit("agent.start", {"agent": ag, "model_id": _model_for(ag, A)})

        def one(ag):
            t0 = time.monotonic()
            try:
                text, grounded, meta = _call_agent(ag, enriched, A)
                return ag, text, grounded, meta, int((time.monotonic() - t0) * 1000), None
            except Exception as e:
                return ag, None, False, {}, int((time.monotonic() - t0) * 1000), str(e)[:160] or type(e).__name__

        ex = ThreadPoolExecutor(max_workers=6)
        futs = {ex.submit(contextvars.copy_context().run, one, ag): ag for ag in AGENTS}
        pending = set(AGENTS)
        t_run = time.monotonic()
        not_done = set(futs)
        try:
            while not_done and time.monotonic() - t_run < AGENT_DEADLINE_S:
                done, not_done = wait(not_done, timeout=1.0, return_when=FIRST_COMPLETED)
                for fut in done:
                    ag, text, grounded, meta, ms, err = fut.result()
                    pending.discard(ag)
                    if err:
                        run.emit("agent.error", {"agent": ag, "reason": err})
                        with L:
                            verified.add(ag)
                    else:
                        display, appended = _split_display(text)
                        answers[ag] = {"text": text, "display": display, "appended": appended, "meta": meta, "latency": ms}
                        run.emit("agent.answer", {"agent": ag, "text": display, "latency_ms": ms, "searched": bool(grounded)})
                        seen, new_urls = [], []
                        with L:
                            for c in A.extract_urls(text):
                                u = c["url"]
                                if u in seen:
                                    continue
                                seen.append(u)
                                pos = display.find(u)
                                cid[0] += 1
                                d = {"agent": ag, "cit_id": cid[0], "url_raw": u, "source": "text" if pos >= 0 else "api"}
                                if pos >= 0:
                                    d["span"] = {"start": pos, "end": pos + len(u)}
                                cits.append(dict(d))
                                run.emit("citation.found", d)
                            by_url = {c["url_raw"]: c["cit_id"] for c in cits if c["agent"] == ag}
                            done_sup = set()
                            for sp in (meta.get("supports") or []):
                                for u in (sp.get("urls") or []):
                                    cid_ = by_url.get(u)
                                    if not cid_ or cid_ in done_sup:
                                        continue
                                    st, en = sp.get("start"), sp.get("end")
                                    if not (isinstance(st, int) and isinstance(en, int) and 0 <= st < en <= len(display)):
                                        needle = (sp.get("claim") or sp.get("text") or "").strip()[:120]
                                        st = display.find(needle) if needle else -1
                                        if st < 0:
                                            continue
                                        en = st + len(needle)
                                    done_sup.add(cid_)
                                    run.emit("citation.support", {"agent": ag, "cit_id": cid_, "span": {"start": st, "end": en}})
                            # resolve now: reuse a result already in, join one in flight, or start one
                            pending_urls[ag] = set()
                            for u in seen:
                                if u in res:
                                    settle(u, res[u])
                                else:
                                    pending_urls[ag].add(u)
                                    if not any(u in s_ for a2, s_ in pending_urls.items() if a2 != ag):
                                        f = rex.submit(_resolve, u, A)
                                        f.add_done_callback(lambda fut, u=u: on_resolved(fut, u))
                            if not pending_urls[ag]:
                                verify_agent(ag)
                # first reading wave once most agents are in and the run is past READ_START_S (checked every tick)
                if not rd["started"] and len(pending) <= 1 and time.monotonic() - t_run >= READ_START_S and len(verified) >= 3:
                    start_reads()
        finally:
            ex.shutdown(wait=False, cancel_futures=True)
        for ag in sorted(pending, key=AGENTS.index):
            run.emit("agent.error", {"agent": ag, "reason": f"no answer in {int(AGENT_DEADLINE_S)} s"})
            with L:
                verified.add(ag)
        # let the last resolves land (bounded), then settle anything still out as a timeout and verify
        t_wait = time.monotonic()
        while time.monotonic() - t_wait < 60 and any(pending_urls.get(ag) for ag in AGENTS):
            time.sleep(0.25)
        with L:
            for ag in AGENTS:
                for u in list(pending_urls.get(ag) or []):
                    settle(u, {"final": u, "kind": "none", "status": "wall", "http": None, "reason": "timeout"})
            for ag in AGENTS:
                verify_agent(ag)
        rex.shutdown(wait=False, cancel_futures=True)
        start_reads(final=True)
        t_wait = time.monotonic()
        while time.monotonic() - t_wait < 75 and any(not f.done() for f in rd["futs"]):
            time.sleep(0.25)
        with L:
            for f, pk in rd["futs"].items():
                if not f.done():
                    p = pages[pk]
                    if p.get("read") is None:
                        p.update(read="blocked", title=None, brand_count=0)
                        rd["blocked"] += 1
                        run.emit("page.read", {"page_key": pk, "status": "blocked", "tier": "direct", "title": None, "byline": None, "date": None, "brand_count": 0, "text_chars": 0, "note": "no response in 75 s"})
        pex.shutdown(wait=False, cancel_futures=True)
        ranked = ranked_pages()
        cap = min(READ_CAP, len(ranked))
        read, blocked = rd["read"], rd["blocked"]

        # classify every distinct root: owned by rule, the rest by the app's classifier (observed roots only)
        roots = list(dict.fromkeys(p["root"] for _, p in ranked))
        types = {}
        for rt in roots:
            try:
                if A._is_brand_own_domain(rt, brand):
                    types[rt] = "owned"
            except Exception:
                pass
        todo = [rt for rt in roots if rt not in types]
        if todo:
            try:
                types.update(A._classify_domains_llm(todo, brand, prompt[:120], None) or {})
            except Exception as e:
                print("one-prompt classify failed:", str(e)[:120])
        for pk, p in ranked:
            p["type"] = types.get(p["root"]) or "unclassified"
            run.emit("page.classified", {"page_key": pk, "source_type": p["type"]})

        est = None
        try:
            est, _rows = A._usage_cost(A._aggregate_usage_rows(sink))
            est = round(float(est), 4)
        except Exception:
            pass
        run.est_cost_usd = est
        run.cost_note = "Meta AI priced at Muse Spark 1.3 list (META_IN_PER_M, META_OUT_PER_M)"
        n_drop = sum(1 for c in cits if c.get("dropped"))
        run.counts = {"answers": len(answers), "citations": len(cits), "distinct_pages": len(ranked), "read": read, "read_cap": cap, "blocked": blocked, "dropped": n_drop}
        run.findings = _findings(run, A, answers, ranked, pages, cap, read, blocked, n_drop, len(cits))
        run.emit("run.done", {"duration_ms": int((time.monotonic() - run.t0) * 1000), "est_cost_usd": est, "counts": run.counts})
        run.emit("findings.preview", run.findings)
    except Exception as e:
        run.failed = f"{type(e).__name__}: {str(e)[:160]}"
        print("one-prompt run failed:", run.failed)
        if run.findings is None:
            run.findings = {"answers": len(answers), "brands_named": [], "citation_mix": {"distinct_pages": 0, "by_type": {}}, "top_sources": [], "editorial_placements": [], "owned_mix": {"brand_pages": 0, "competitor_pages": 0, "distinct_pages": 0}, "error": run.failed}
        run.emit("run.done", {"duration_ms": int((time.monotonic() - run.t0) * 1000), "est_cost_usd": run.est_cost_usd, "counts": run.counts or {"answers": len(answers), "citations": len(cits), "distinct_pages": 0, "read": 0, "read_cap": 0, "blocked": 0, "dropped": 0}, "error": run.failed})
    finally:
        run.emit("findings.locked", {})
        if slot_release:
            try:
                slot_release()
            except Exception:
                pass


def _findings(run, A, answers, ranked, pages, cap, read, blocked, n_drop, n_cits):
    brand = run.brand
    n = len(answers)
    # brands named: the audited brand plus the other brands the answers name, found by one Haiku pass
    # over the answers and kept only when the name appears in the answer text (observed names only)
    others = []
    try:
        joined = "\n\n".join(f"[{ag}]\n{a['display'][:6000]}" for ag, a in answers.items())
        resp = A._claude_msg(model=A.CLAUDE_HAIKU, max_tokens=400, messages=[{"role": "user", "content":
            f'These are {n} AI answers to the question "{run.prompt}". List the brand or company names the answers put forward as options '
            f'(products and makers, as written in the text), other than "{brand}". Respond with ONLY a JSON list of strings, most mentioned first, at most 12.\n\n{joined}'}])
        m = re.search(r"\[.*\]", resp.content[0].text, re.S)
        cand = json.loads(m.group()) if m else []
        others = [str(x).strip() for x in cand if isinstance(x, str) and 1 < len(str(x).strip()) <= 40]
    except Exception as e:
        print("one-prompt brand pass failed:", str(e)[:120])
    texts = {ag: a["display"] for ag, a in answers.items()}

    def pos(name, t):
        m = re.search(r"(?<![A-Za-z0-9])" + re.escape(name) + r"(?![A-Za-z0-9])", t, re.I)
        return m.start() if m else -1
    names = [brand] + [o for o in others if o.lower() != brand.lower()]
    rows = {}
    for nm in names:
        named_in = [ag for ag, t in texts.items() if pos(nm, t) >= 0]
        if nm != brand and not named_in:
            continue
        rows[nm] = {"name": nm, "named_in": named_in, "named_first_in": []}
    for ag, t in texts.items():
        first = min(((pos(nm, t), nm) for nm in rows if pos(nm, t) >= 0), default=None)
        if first:
            rows[first[1]]["named_first_in"].append(ag)
    allroots = [p["root"] for _, p in ranked]

    def brand_domain(nm):
        key = re.sub(r"[^a-z0-9]", "", nm.lower())
        for rt in allroots:
            if key and key in rt.replace("-", ""):
                return rt
        return None
    for r in rows.values():
        r["domain"] = brand_domain(r["name"])
    brands_named = sorted(rows.values(), key=lambda r: (r["name"] != brand, -len(r["named_in"])))[:8]
    by_type = {}
    for _, p in ranked:
        by_type[p["type"]] = by_type.get(p["type"], 0) + 1
    roots = {}
    for _, p in ranked:
        r = roots.setdefault(p["root"], {"root": p["root"], "answers": set(), "pages": 0})
        r["answers"] |= p["agents"]
        r["pages"] += 1
    top = sorted(roots.values(), key=lambda r: (-len(r["answers"]), -r["pages"]))[:6]
    editorial = sorted([{"url": p["url"], "title": (p.get("title") or pk)[:120], "outlet": p["root"], "answers": len(p["agents"])}
                        for pk, p in ranked if p["type"] == "editorial"], key=lambda e: -e["answers"])[:6]
    owned = sum(1 for _, p in ranked if p["type"] == "owned")
    comp = sum(1 for _, p in ranked if p["type"] == "competitor")
    return {"answers": n, "brands_named": brands_named,
            "citation_mix": {"distinct_pages": len(ranked), "by_type": by_type},
            "top_sources": [{"root": r["root"], "answers": len(r["answers"]), "pages": r["pages"]} for r in top],
            "editorial_placements": editorial,
            "owned_mix": {"brand_pages": owned, "competitor_pages": comp, "distinct_pages": len(ranked)},
            "pages": {"distinct_pages": len(ranked), "read_cap": cap, "read": read, "blocked": blocked, "dropped": n_drop, "citations": n_cits}}


def start(run, A, slot_release=None):
    t = threading.Thread(target=execute, args=(run, A, slot_release), daemon=True)
    t.start()
    return t
