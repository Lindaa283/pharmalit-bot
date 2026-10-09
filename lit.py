import aiohttp, re, json, os, time
EU="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError: pass
BASE=os.environ.get("LLM_GATEWAY_BASE_URL","http://127.0.0.1:4000/v1").rstrip("/")
GW=BASE+"/chat/completions"
def _key():
    k=os.environ.get("LLM_GATEWAY_KEY")
    if k: return k.strip()
    fb=os.environ.get("LLM_GATEWAY_KEY_FILE",os.path.expanduser("~/.llm_gateway_key"))
    for f in (fb,"/workspace/llm-gateway/.master_key"):
        if os.path.exists(f): return open(f).read().strip()
    raise RuntimeError("LLM_GATEWAY_KEY not set")
KEY=_key()
NCBI=os.environ.get("NCBI_API_KEY")
def _ep(d):
    if NCBI: d["api_key"]=NCBI
    return d
DISC="*AI-generated literature summary, not medical advice.*"
async def pubmed(s, q, n=5):
    async with s.get(EU+"esearch.fcgi", params=_ep(dict(db="pubmed",term=q,retmax=n,sort="pub_date",retmode="json",tool="pharmalit"))) as r:
        ids=(await r.json())["esearchresult"]["idlist"]
    if not ids: return []
    async with s.get(EU+"efetch.fcgi", params=_ep(dict(db="pubmed",id=",".join(ids),rettype="abstract",retmode="xml"))) as r:
        x=await r.text()
    out=[]
    for a in re.findall(r"<PubmedArticle>.*?</PubmedArticle>", x, re.S):
        pm=re.search(r"<PMID[^>]*>(\d+)",a).group(1)
        t=re.sub("<[^>]+>","",(re.search(r"<ArticleTitle>(.*?)</ArticleTitle>",a,re.S) or [None,""])[1])
        ab=" ".join(re.sub("<[^>]+>","",m) for m in re.findall(r"<AbstractText[^>]*>(.*?)</AbstractText>",a,re.S))
        out.append(dict(pmid=pm,title=t,abstract=ab[:2500]))
    return out
async def chat(s, model, prompt, mt=600):
    async with s.post(GW, headers={"Authorization":"Bearer "+KEY}, json=dict(model=model,messages=[{"role":"user","content":prompt}],max_tokens=mt,temperature=0.2), timeout=aiohttp.ClientTimeout(total=120)) as r:
        return (await r.json())["choices"][0]["message"]["content"].strip()
async def lit(target):
    async with aiohttp.ClientSession() as s:
        arts=await pubmed(s,target)
        if not arts: return f"No PubMed results for **{target}**.\n{DISC}"
        ctx="\n\n".join(f"[PMID {a['pmid']}] {a['title']}\n{a['abstract']}" for a in arts)
        p=f"Using ONLY these PubMed abstracts, summarise the latest findings on '{target}' in 5 bullets. Cite every claim as [PMID]. \n\n{ctx}"
        sums={}
        for m in ("deepseek-chat","glm-4-flash"):
            try: sums[m]=await chat(s,m,p)
            except Exception as e: sums[m]=f"(failed: {type(e).__name__})"
        mp=(f"Merge these two summaries about '{target}' into one concise English answer (max 1200 characters): key findings, then agreements/gaps. Keep [PMID] citations, invent none.\n\n"+"\n\n".join(f"{k}:\n{v}" for k,v in sums.items()))
        merged=await chat(s,"deepseek-chat",mp,700)
    links=" ".join(f"[{a['pmid']}](<https://pubmed.ncbi.nlm.nih.gov/{a['pmid']}/>)" for a in arts)
    return f"**/lit {target}**\n{merged[:1500]}\n\nSources: {links}\n{DISC}"[:1990]
QF=os.path.join(os.path.dirname(os.path.abspath(__file__)),"lit_quota.json")
def take_quota(uid, limit=3):
    d=json.load(open(QF)) if os.path.exists(QF) else {}
    day=time.strftime("%Y-%m-%d")
    if d.get("day")!=day: d={"day":day,"u":{}}
    c=d["u"].get(str(uid),0)
    if c>=limit: return False
    d["u"][str(uid)]=c+1; json.dump(d,open(QF,"w")); return True
