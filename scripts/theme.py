"""Re-tema dos SVGs do README (header, cards, botões).

Lê sempre a versão original (commit 06118db) e reaplica cor + efeitos, então pode rodar quantas vezes quiser:
    python3 scripts/theme.py violeta assets     # opções: violeta, azul, sunset
"""
import re, subprocess, sys, pathlib
BASE = "06118db"
THEMES = {
  "violeta": dict(A="#A78BFA", B="#22D3EE", dim="#251E45"),
  "azul":    dict(A="#60A5FA", B="#34D399", dim="#16294A"),
  "sunset":  dict(A="#F472B6", B="#FB923C", dim="#3F1830"),
}
NEUTRAL = {"#0A0A0B":"#08080D","#111113":"#0E0E16","#232327":"#22222F","#34343A":"#33334A",
           "#56565C":"#5A5A70","#8C8C93":"#9090A6","#F4F4F2":"#F4F4FA"}
FILES = ["header","card-finsight","card-enduro","card-datapulse","card-olist","btn-linkedin","btn-portfolio","btn-email"]

def src(name):
    return subprocess.check_output(["git","show",f"{BASE}:assets/{name}.svg"], text=True)

def recolor(s, t):
    m = dict(NEUTRAL); m.update({"#D4FF3A": t["A"], "#3B4714": t["dim"]})
    return re.sub(r"#[0-9A-Fa-f]{6}\b", lambda x: m.get(x.group(0).upper(), x.group(0)), s)

def grad(id_, t, x1, x2, y1=0, y2=0, user=True):
    u = ' gradientUnits="userSpaceOnUse"' if user else ''
    return (f'<linearGradient id="{id_}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{u}>'
            f'<stop offset="0" stop-color="{t["A"]}"/><stop offset="1" stop-color="{t["B"]}"/></linearGradient>')

def header(s, t):
    A, B = t["A"], t["B"]
    defs = (grad("gname", t, 44, 470) + grad("gcells", t, 744, 920) +
            f'<linearGradient id="gborder" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{A}" stop-opacity=".7"/>'
            f'<stop offset=".35" stop-color="{A}" stop-opacity="0"/><stop offset=".7" stop-color="{B}" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="{B}" stop-opacity=".6"/></linearGradient>'
            f'<radialGradient id="au1"><stop offset="0" stop-color="{A}" stop-opacity=".38"/><stop offset="1" stop-color="{A}" stop-opacity="0"/></radialGradient>'
            f'<radialGradient id="au2"><stop offset="0" stop-color="{B}" stop-opacity=".22"/><stop offset="1" stop-color="{B}" stop-opacity="0"/></radialGradient>'
            '<clipPath id="clip"><rect width="1000" height="460" rx="20"/></clipPath>'
            '<linearGradient id="scan" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".07"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            '<clipPath id="pclip"><rect x="616" y="96" width="336" height="300" rx="14"/></clipPath>')
    s = s.replace("<defs>", "<defs>" + defs, 1)
    css = ('.d1{animation:d1 14s ease-in-out infinite alternate}@keyframes d1{to{transform:translate(-120px,60px)}}'
           '.d2{animation:d2 18s ease-in-out infinite alternate}@keyframes d2{to{transform:translate(140px,-50px)}}'
           '.sc{animation:sc 4.5s ease-in-out infinite}@keyframes sc{0%{transform:translateX(-200px)}60%,100%{transform:translateX(560px)}}')
    s = s.replace("</style>", css + "</style>", 1)
    # aurora no lugar do brilho chapado
    s = re.sub(r'<circle cx="790" cy="230" r="260" fill="url\(#glow\)"/>',
               '<g clip-path="url(#clip)"><ellipse class="d1" cx="820" cy="120" rx="380" ry="260" fill="url(#au1)"/>'
               '<ellipse class="d2" cx="420" cy="470" rx="420" ry="240" fill="url(#au2)"/></g>', s)
    # borda em gradiente por cima do contorno
    s = s.replace('<text x="48" y="58"', '<rect x=".5" y=".5" width="999" height="459" rx="20" fill="none" stroke="url(#gborder)"/><text x="48" y="58"', 1)
    # nome com gradiente
    s = re.sub(r'(<text x="44" y="288"[^>]*fill=")[^"]+(")', r'\1url(#gname)\2', s)
    s = re.sub(r'Cavalchi<tspan class="g6" fill="[^"]+">\.</tspan>', 'Cavalchi.', s)
    # células ok com gradiente horizontal; painel com vidro + varredura
    s = s.replace(f'fill="{A}" opacity=".92"', 'fill="url(#gcells)"')
    s = re.sub(r'(@keyframes k\d\{[^@]*?)(15|26|37|48|59)%,90%\{fill:' + A, lambda m: m.group(1)+m.group(2)+'%,90%{fill:url(#gcells)', s)
    s = s.replace('<text x="636" y="128"', '<rect class="sc" x="616" y="96" width="200" height="300" fill="url(#scan)" clip-path="url(#pclip)"/><text x="636" y="128"', 1)
    s = s.replace('<rect x="636" y="360" width="10" height="10" rx="2" fill="'+A+'"/>', '<rect x="636" y="360" width="10" height="10" rx="2" fill="url(#gcells)"/>')
    return s

def card(s, t, name):
    A, B = t["A"], t["B"]
    defs = (f'<defs><radialGradient id="cg" cx="1" cy="0" r="1"><stop offset="0" stop-color="{A}" stop-opacity=".16"/>'
            f'<stop offset=".6" stop-color="{B}" stop-opacity=".04"/><stop offset="1" stop-color="{B}" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="ce" x1="0" x2="1"><stop offset="0" stop-color="{A}" stop-opacity="0"/><stop offset=".5" stop-color="{A}"/>'
            f'<stop offset="1" stop-color="{B}" stop-opacity="0"/></linearGradient>' + grad("ca", t, 28, 452) + '</defs>')
    bg = re.search(r'<rect x="\.5" y="\.5" width="479" height="319" rx="18"[^>]*/>', s).group(0)
    s = s.replace(bg, defs + bg + '<rect x=".5" y=".5" width="479" height="319" rx="18" fill="url(#cg)"/>'
                  '<line x1="60" y1=".75" x2="420" y2=".75" stroke="url(#ce)" stroke-width="1.5" opacity=".8"/>', 1)
    s = s.replace(f'stroke="{A}" stroke-width="2"', 'stroke="url(#ca)" stroke-width="2.5"')  # linha do enduro
    s = s.replace(f'<circle cx="38" cy="176" r="9" fill="{A}"', '<circle cx="38" cy="176" r="9" fill="url(#ca)"')
    for x in (160, 262, 392):
        s = s.replace(f'<circle cx="{x}" cy="176" r="9" fill="{A}"', f'<circle cx="{x}" cy="176" r="9" fill="url(#ca)"')
    return s

def btn(s, t):
    A, B = t["A"], t["B"]
    g = grad("bg", t, 0, 188)
    return s.replace(f'fill="{A}" stroke="{A}"', 'fill="url(#bg)" stroke="none"').replace("</style>", "</style><defs>"+g+"</defs>", 1)

def build(theme, outdir):
    t = THEMES[theme]; out = pathlib.Path(outdir); out.mkdir(parents=True, exist_ok=True)
    for n in FILES:
        s = recolor(src(n), t)
        if n == "header": s = header(s, t)
        elif n.startswith("card"): s = card(s, t, n)
        elif n == "btn-linkedin": s = btn(s, t)
        (out / f"{n}.svg").write_text(s)

if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
