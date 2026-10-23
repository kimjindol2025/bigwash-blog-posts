#!/usr/bin/env python3
"""posts/*.txt 와 posts/images/ 로 index.html, p/*.html, README.md 를 다시 만듭니다."""
import os, re, html, glob, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "posts"); IMG = os.path.join(P, "images")
ALIAS = {"2026-10-11-coupang-eats-outage-compensation": "coupang"}
imgs = sorted(os.listdir(IMG)) if os.path.isdir(IMG) else []
def images_for(slug):
    pre = ALIAS.get(slug, slug) + "-"
    return [f for f in imgs if f.startswith(pre) and f.lower().endswith((".jpg",".jpeg",".png",".webp"))]
posts = []
for f in sorted(glob.glob(os.path.join(P, "*.txt")), reverse=True):
    slug = os.path.basename(f)[:-4]
    lines = open(f, encoding="utf-8").read().strip().splitlines()
    title = lines[0].strip() if lines else slug
    body = "\n".join(lines[1:]).strip()
    paras = [x.strip() for x in re.split(r"\n\s*\n", body) if x.strip()]
    posts.append(dict(slug=slug, date=slug[:10], title=title, paras=paras, imgs=images_for(slug)))
CSS = """body{margin:0;font-family:-apple-system,'Apple SD Gothic Neo','Noto Sans KR','Malgun Gothic',sans-serif;background:#f4f7fa;color:#222;line-height:1.75}
header{background:#0b5cad;color:#fff;padding:22px 16px;text-align:center}header a{color:#fff;text-decoration:none}
h1{margin:0;font-size:1.5em}.sub{opacity:.85;font-size:.9em}main{max-width:760px;margin:0 auto;padding:16px}
.card{background:#fff;border-radius:12px;box-shadow:0 1px 4px rgba(0,0,0,.08);margin:0 0 16px;overflow:hidden}
.card a{color:inherit;text-decoration:none}.card img{width:100%;display:block;max-height:340px;object-fit:cover}
.card .t{padding:12px 16px}.card h2{font-size:1.1em;margin:0 0 6px}.date{color:#0b5cad;font-size:.85em}
.ex{color:#555;font-size:.92em;margin:6px 0 0}article{background:#fff;border-radius:12px;padding:18px}
article img{width:100%;border-radius:8px;margin:12px 0}article h1{font-size:1.35em;color:#111}
.back{display:inline-block;margin:8px 0 14px;color:#0b5cad}footer{text-align:center;color:#888;font-size:.8em;padding:20px}"""
def page(title, inner, depth=0):
    up = "../" * depth
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><style>{CSS}</style></head><body>
<header><a href="{up}index.html"><h1>빅워시 블로그</h1></a><div class="sub">세차장 소식과 생활 뉴스 정리</div></header>
<main>{inner}</main><footer>마지막 업데이트 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} (한국 시간)</footer></body></html>"""
os.makedirs(os.path.join(ROOT, "p"), exist_ok=True)
cards = []
for p in posts:
    e = html.escape
    thumb = f'<img loading="lazy" src="posts/images/{p["imgs"][0]}" alt="">' if p["imgs"] else ""
    ex = e(p["paras"][0][:110]) + "…" if p["paras"] else ""
    cards.append(f'<div class="card"><a href="p/{p["slug"]}.html">{thumb}<div class="t"><div class="date">{p["date"]}</div><h2>{e(p["title"])}</h2><p class="ex">{ex}</p></div></a></div>')
    # 본문 사이에 그림을 고르게 배치
    body, ims, n = [], list(p["imgs"]), len(p["paras"])
    if ims: body.append(f'<img src="../posts/images/{ims.pop(0)}" alt="">')
    step = max(1, n // (len(ims) + 1)) if ims else 0
    for i, para in enumerate(p["paras"]):
        body.append("<p>" + e(para).replace("\n", "<br>") + "</p>")
        if ims and step and (i + 1) % step == 0: body.append(f'<img loading="lazy" src="../posts/images/{ims.pop(0)}" alt="">')
    for im in ims: body.append(f'<img loading="lazy" src="../posts/images/{im}" alt="">')
    art = f'<a class="back" href="../index.html">← 글 목록</a><article><div class="date">{p["date"]}</div><h1>{e(p["title"])}</h1>{"".join(body)}</article>'
    open(os.path.join(ROOT, "p", p["slug"] + ".html"), "w", encoding="utf-8").write(page(p["title"], art, 1))
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(page("빅워시 블로그", f'<p>전체 글 {len(posts)}편, 최신 글이 위에 있습니다.</p>' + "".join(cards)))
rd = ["# 빅워시 블로그 기록", "", "구글 뉴스와 세차장 소식을 정리한 블로그 글 모음입니다. 하루 세 번 새 글이 추가됩니다.", "",
      "웹페이지: https://kimjindol2025.github.io/bigwash-blog-posts/", "", f"전체 글 {len(posts)}편", "",
      "| 날짜 | 제목 | 그림 | 링크 |", "|---|---|---|---|"]
for p in posts:
    t = p["title"].replace("|", "/")
    rd.append(f'| {p["date"]} | {t} | {len(p["imgs"])}장 | [글 보기](https://kimjindol2025.github.io/bigwash-blog-posts/p/{p["slug"]}.html) · [원문](posts/{p["slug"]}.txt) |')
rd += ["", "## 업데이트 방법", "", "posts 폴더에 글(.txt)과 posts/images 폴더에 그림을 넣고 `python3 scripts/build.py` 를 실행한 뒤 커밋하고 푸시합니다."]
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write("\n".join(rd) + "\n")
print(f"built {len(posts)} posts, {sum(len(p['imgs']) for p in posts)} images linked")
