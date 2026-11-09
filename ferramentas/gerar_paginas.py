#!/usr/bin/env python3
"""Gera as páginas estáticas das notícias (para o Google), o sitemap.xml e o robots.txt.

Uso (na raiz do repositório): python3 ferramentas/gerar_paginas.py
Lê noticias.json e (re)cria:
  noticias/<id>.html   – uma página por notícia, com título, descrição e dados estruturados
  noticias/index.html  – lista de todas as notícias
  sitemap.xml, robots.txt
Não altera index.html, d/ nem CNAME.
"""
import datetime, html, json, os, re, shutil, urllib.parse

SITE = 'https://rafaelmsouza.adv.br'
UMAMI = 'e1ed7d73-fa33-4e80-996a-a7cae57abea0'
WA = '5514996119228'
AUTOR = 'Rafael de Mello Souza'
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
e = html.escape

CSS = """*{box-sizing:border-box}body{margin:0;background:#f7f3ea;color:#1b2333;font:17px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:#1e3d78}header{background:#0f1e3a;color:#efe6d2;padding:16px 20px;display:flex;align-items:center;gap:14px}
header img{width:44px;height:44px;border-radius:8px}header a{color:inherit;text-decoration:none}.n{font-family:Georgia,serif;font-size:19px}.o{font-size:12px;letter-spacing:2px;color:#b9c6e4}
nav{background:#1e3d78;display:flex;overflow-x:auto;padding:0 8px}nav a{color:#dfe7f6;text-decoration:none;padding:11px 12px;font-size:15px;white-space:nowrap}
main{max-width:720px;margin:0 auto;padding:22px 16px 110px}article,.card{background:#fff;border:1px solid #e3dccb;border-radius:16px;padding:22px}
h1{font-family:Georgia,serif;color:#0f1e3a;font-size:28px;line-height:1.25;margin:4px 0 10px}h2{font-family:Georgia,serif;color:#0f1e3a;font-size:20px;margin:0 0 4px}
.d{color:#5d6676;font-size:14px;font-weight:600}.sub{color:#5d6676;font-size:14px}.btn{display:inline-block;background:#1f9d55;color:#fff;text-decoration:none;font-weight:700;padding:12px 18px;border-radius:10px;margin:10px 8px 0 0}
.btn.s{background:#fff;color:#0f1e3a;border:1px solid #e3dccb}.lista a{text-decoration:none}.lista div{border-top:1px solid #e3dccb;padding:14px 0}.lista div:first-child{border-top:0}
footer{text-align:center;font-size:13px;color:#5d6676;padding:10px 16px 30px}"""


def cab(titulo, desc, url, extra=''):
    return f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{url}">
<meta property="og:type" content="article"><meta property="og:title" content="{e(titulo)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}/cartao.jpg"><meta property="og:locale" content="pt_BR">
<link rel="icon" href="/icon.png"><meta name="theme-color" content="#0f1e3a">
<script defer src="https://cloud.umami.is/script.js" data-website-id="{UMAMI}"></script>{extra}
<style>{CSS}</style></head><body>
<header><a href="/"><img src="/icon.png" alt=""></a><a href="/"><div class="n">Rafael de Mello Souza</div><div class="o">ADVOGADO · OAB/SP 352.797</div></a></header>
<nav><a href="/#inicio">Início</a><a href="/#quem-somos">Quem somos</a><a href="/noticias/">Notícias</a><a href="/#consulta">Consultar processo</a></nav><main>"""


ROD = f"""</main><footer>Rafael de Mello Souza · Advogado · OAB/SP nº 352.797<br>© 2026 Rafael de Mello Souza – Advocacia. Todos os direitos reservados.<br>Conteúdo informativo, não constitui consultoria jurídica. Cada caso tem particularidades. · <a href="/privacidade.html">Privacidade</a></footer></body></html>"""


def resumo(t, n=155):
    t = re.sub(r'\s+', ' ', t).strip()
    return t if len(t) <= n else t[:n].rsplit(' ', 1)[0] + '…'


def main():
    ns = sorted(json.load(open(os.path.join(RAIZ, 'noticias.json'), encoding='utf-8')), key=lambda n: n['data'], reverse=True)
    pasta = os.path.join(RAIZ, 'noticias')
    if os.path.isdir(pasta):
        shutil.rmtree(pasta)
    os.makedirs(pasta)
    for n in ns:
        url = f"{SITE}/noticias/{n['id']}.html"
        desc = resumo(n['texto'])
        ld = {"@context": "https://schema.org", "@type": "NewsArticle", "headline": n['titulo'][:110], "description": desc,
              "datePublished": n['data'], "dateModified": n['data'], "inLanguage": "pt-BR", "mainEntityOfPage": url, "image": [f"{SITE}/cartao.jpg"],
              "author": {"@type": "Person", "name": AUTOR, "jobTitle": "Advogado", "url": SITE},
              "publisher": {"@type": "Organization", "name": f"{AUTOR} – Advocacia", "logo": {"@type": "ImageObject", "url": f"{SITE}/icon.png"}}}
        corpo = ''.join(f'<p>{e(p)}</p>' for p in str(n['texto']).split('\n') if p.strip())
        fonte = f'<p class="sub">Fonte: <a href="{e(n["fonte"])}" target="_blank" rel="noopener nofollow" data-umami-event="noticia-fonte">{e(n.get("fonteNome") or "link")}</a></p>' if n.get('fonte') else ''
        d = n['data']
        wa = e(f"https://wa.me/{WA}?text=" + urllib.parse.quote(f"Olá, Dr. Rafael! Li a notícia \"{n['titulo']}\" no seu site e tenho uma dúvida."))
        pag = cab(f"{n['titulo']} | Rafael de Mello Souza – Advogado", desc, url, f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>') + f"""
<article><div class="d">{d[8:10]}/{d[5:7]}/{d[:4]} · Notícias</div><h1>{e(n['titulo'])}</h1>{corpo}{fonte}
<a class="btn" href="{wa}" target="_blank" rel="noopener" data-umami-event="whatsapp">💬 Tirar dúvida no WhatsApp</a><a class="btn s" href="/noticias/">Ver todas as notícias</a></article>""" + ROD
        open(os.path.join(pasta, n['id'] + '.html'), 'w', encoding='utf-8').write(pag)
    lista = ''.join(f'<div><span class="d">{n["data"][8:10]}/{n["data"][5:7]}/{n["data"][:4]}</span><h2><a href="/noticias/{n["id"]}.html">{e(n["titulo"])}</a></h2><span class="sub">{e(resumo(n["texto"], 180))}</span></div>' for n in ns)
    open(os.path.join(pasta, 'index.html'), 'w', encoding='utf-8').write(
        cab('Notícias sobre INSS e Direito Previdenciário | Rafael de Mello Souza – Advogado', 'Notícias curtas sobre INSS, aposentadorias, BPC/LOAS e Direito Previdenciário, publicadas toda segunda, quarta e sexta pelo advogado Rafael de Mello Souza (OAB/SP 352.797).', f'{SITE}/noticias/')
        + f'<div class="card"><h1>Notícias</h1><p class="sub">INSS e Direito Previdenciário, toda segunda, quarta e sexta.</p><div class="lista">{lista}</div></div>' + ROD)
    priv = os.path.join(RAIZ, 'ferramentas', 'privacidade.html')
    if os.path.exists(priv):
        open(os.path.join(RAIZ, 'privacidade.html'), 'w', encoding='utf-8').write(
            cab('Política de Privacidade | Rafael de Mello Souza – Advogado', 'Como o site rafaelmsouza.adv.br trata dados pessoais, conforme a LGPD.', f'{SITE}/privacidade.html')
            + '<article>' + open(priv, encoding='utf-8').read() + '</article>' + ROD)
    hoje = datetime.date.today().isoformat()
    urls = [(f'{SITE}/', hoje, '1.0'), (f'{SITE}/noticias/', ns[0]['data'] if ns else hoje, '0.8')] + [(f"{SITE}/noticias/{n['id']}.html", n['data'], '0.6') for n in ns] + [(f'{SITE}/privacidade.html', hoje, '0.2')]
    open(os.path.join(RAIZ, 'sitemap.xml'), 'w', encoding='utf-8').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + ''.join(f'  <url><loc>{u}</loc><lastmod>{m}</lastmod><priority>{p}</priority></url>\n' for u, m, p in urls) + '</urlset>\n')
    open(os.path.join(RAIZ, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nDisallow: /d/\n\nSitemap: {SITE}/sitemap.xml\n')
    print(f'{len(ns)} notícias; sitemap com {len(urls)} endereços')


if __name__ == '__main__':
    main()
