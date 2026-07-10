# 🤖 Subgraphs & Agents (LangGraph) — SpyFy

Implementação de cada agente como **subgraph** componível. Todos operam sobre `OfferState` (ver [langgraph-architecture.md](langgraph-architecture.md)).

## Tools compartilhadas (LangChain)

```python
from langchain_core.tools import tool

@tool
async def scrape_network(network: str, niche: str, country: str) -> list[dict]:
    """Coleta anúncios de uma rede (meta/tiktok/google) por nicho e país."""
    return await scraper_client.collect(network, niche, country)

@tool
async def headless_fetch(url: str, geo: str = "BR") -> str:
    """Renderiza uma página (SPA-safe) e retorna HTML final + network log."""
    return await browser_pool.render(url, geo=geo)

@tool
async def download_asset(url: str) -> dict:
    """Baixa um asset (img/css/js/fonte) e retorna o caminho no R2."""
    return await assets.download(url)

@tool
def detect_stack(html: str, network_log: list) -> dict:
    """Detecta checkout, builder e pixels (fingerprint)."""
    return fingerprint.analyze(html, network_log)

@tool
async def transcribe_vsl(video_url: str) -> dict:
    """Transcreve VSL (Whisper) e estrutura (hook/problema/solução/CTA)."""
    return await asr.transcribe_and_structure(video_url)

@tool
def extract_copy(html: str) -> dict:
    """Extrai headline, bullets, CTA, garantia, provas (LLM structured)."""
    return copy_extractor.run(html)

@tool
async def embed(text: str) -> list[float]:
    """Gera embedding para busca semântica/dedup."""
    return await embeddings.create(text)
```

---

## 1. Scout Subgraph (descoberta)

```python
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

def scout_agent(state):
    llm = ChatAnthropic(model="claude-haiku").bind_tools([scrape_network])
    resp = llm.invoke(scout_prompt(state))
    return {"messages": [resp]}

def collect_results(state):
    ads = state["messages"][-1].content
    return {"discovered_ads": ads,
            "events": [{"type": "ads_discovered", "count": len(ads)}]}

sg = StateGraph(OfferState)
sg.add_node("scout_agent", scout_agent)
sg.add_node("tools", ToolNode([scrape_network]))
sg.add_node("collect", collect_results)
sg.add_edge(START, "scout_agent")
sg.add_conditional_edges("scout_agent",
    lambda s: "tools" if s["messages"][-1].tool_calls else "collect")
sg.add_edge("tools", "scout_agent")
sg.add_edge("collect", END)
scout_subgraph = sg.compile()
```

---


---

## 3. Cloner Subgraph (clonagem de funil em tempo real)

```python
async def fetch_lp(state):
    html = await headless_fetch(state["landing_url"])
    return {"events": [{"type": "lp_fetched"}], "_html": html}

async def grab_assets(state):
    urls = extract_asset_urls(state["_html"])
    saved = [await download_asset(u) for u in urls]
    return {"assets": saved, "events": [{"type": "assets_saved", "n": len(saved)}]}

def fingerprint_stack(state):
    stack = detect_stack(state["_html"], state.get("_netlog", []))
    return {"stack": stack, "events": [{"type": "stack_detected", "stack": stack}]}

async def map_funnel(state):
    steps = await funnel_walker.walk(state["landing_url"], state["stack"])
    return {"funnel_steps": steps,
            "events": [{"type": "funnel_mapped", "steps": len(steps)}]}

def extract_page_copy(state):
    return {"copy": extract_copy(state["_html"]),
            "events": [{"type": "copy_extracted"}]}

async def package_bundle(state):
    url = await packager.bundle(state["assets"], state["_html"], state["funnel_steps"])
    return {"clone_bundle_url": url, "events": [{"type": "clone_ready", "url": url}]}

cg = StateGraph(OfferState)
for name, fn in [("fetch_lp",fetch_lp),("grab_assets",grab_assets),
                 ("fingerprint",fingerprint_stack),("map_funnel",map_funnel),
                 ("extract_copy",extract_page_copy),("package",package_bundle)]:
    cg.add_node(name, fn)
cg.add_edge(START, "fetch_lp")
cg.add_edge("fetch_lp", "grab_assets")
cg.add_edge("grab_assets", "fingerprint")
cg.add_edge("fingerprint", "map_funnel")
cg.add_edge("map_funnel", "extract_copy")
cg.add_edge("extract_copy", "package")
cg.add_edge("package", END)
cloner_subgraph = cg.compile()
```

Cada nó emite `events`, transmitidos via streaming para a UI (ver [realtime-cloning.md](realtime-cloning.md)).

---

## 4. Analyst Subgraph

```python
def analyze(state):
    metrics = analytics.compute(state["discovered_ads"])
    scaling = analytics.scaling_signal(state["discovered_ads"])
    return {"events": [{"type": "analyzed", "scaling": scaling}],
            "messages": [("assistant", str(metrics))]}

ag = StateGraph(OfferState)
ag.add_node("analyze", analyze)
ag.add_edge(START, "analyze"); ag.add_edge("analyze", END)
analyst_subgraph = ag.compile()
```

---

## 5. Guard/QA Subgraph (reflexão)

```python
def qa_check(state):
    score = qa.visual_diff(state["clone_bundle_url"], state["landing_url"])
    ok = score >= 0.95
    return {"confidence": score, "needs_human": not ok,
            "events": [{"type": "qa", "fidelity": score, "passed": ok}]}

def decide(state):
    return END if state["confidence"] >= 0.95 else "escalate"

def escalate(state):
    return {"needs_human": True,
            "messages": [("assistant", "Baixa fidelidade — revisão humana")]}

qg = StateGraph(OfferState)
qg.add_node("qa_check", qa_check)
qg.add_node("escalate", escalate)
qg.add_edge(START, "qa_check")
qg.add_conditional_edges("qa_check", decide, {"escalate":"escalate", END:END})
qg.add_edge("escalate", END)
guard_subgraph = qg.compile()
```

---

## Padrões aplicados

| Padrão | Onde | Benefício |
|--------|------|-----------|
| Supervisor | grafo raiz | roteamento inteligente |
| Subgraphs | cada agente | componibilidade e teste isolado |
| Map-Reduce (Send) | Enricher | paralelismo |
| ReAct (tool loop) | Scout | uso de ferramentas |
| Reflection | Guard | qualidade antes de finalizar |
| Human-in-the-loop | interrupt + Guard | segurança em baixa confiança |

## Testes de agents

- Unit por tool (mock de rede).
- Testes de subgraph com estado fixo (fixtures de HTML).
- Evals end-to-end (dataset de ofertas rotuladas) — ver [ml-models.md](ml-models.md).
- Tracing no LangSmith para regressão.

## 2. Enricher Subgraph (map-reduce paralelo)

```python
from langgraph.constants import Send

def fanout_enrich(state) -> list[Send]:
    return [Send("enrich_one", {"ad": ad}) for ad in state["discovered_ads"]]

async def enrich_one(state):
    ad = state["ad"]
    copy = extract_copy(ad["html"]) if ad.get("html") else {}
    transcript = await transcribe_vsl(ad["video"]) if ad.get("video") else {}
    await embed((copy.get("headline","") + " " + str(transcript)))
    return {"events": [{"type": "ad_enriched", "ad_id": ad["id"]}],
            "copy": copy, "transcript": transcript}

eg = StateGraph(OfferState)
eg.add_node("enrich_one", enrich_one)
eg.add_conditional_edges(START, fanout_enrich, ["enrich_one"])
eg.add_edge("enrich_one", END)
enricher_subgraph = eg.compile()
```
