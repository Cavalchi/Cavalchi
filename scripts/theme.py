"""Re-tema dos SVGs do README (header, cards, botões).

Lê sempre a versão original (commit 06118db) e reaplica cor + efeitos, então pode rodar quantas vezes quiser:
    python3 scripts/theme.py violeta assets     # opções: rosso, mp4 (claro), violeta, azul, sunset, mclaren
"""
import re, subprocess, sys, pathlib
BASE = "06118db"
THEMES = {
  "violeta": dict(A="#A78BFA", B="#22D3EE", dim="#251E45"),
  "azul":    dict(A="#60A5FA", B="#34D399", dim="#16294A"),
  "sunset":  dict(A="#F472B6", B="#FB923C", dim="#3F1830"),
  # vermelho Marlboro da McLaren MP4/4: vermelho no destaque, branco/prata nas execuções ok
  # (assim a única célula vermelha do painel continua sendo a falha)
  "mclaren": dict(A="#E4002B", B="#FF4B2B", dim="#3A0A12", C1="#FFFFFF", C2="#B9BCC8", fail="#FF2E4D"),
}
NEUTRAL = {"#0A0A0B":"#08080D","#111113":"#0E0E16","#232327":"#22222F","#34343A":"#33334A",
           "#56565C":"#5A5A70","#8C8C93":"#9090A6","#F4F4F2":"#F4F4FA"}
FILES = ["header","card-finsight","card-enduro","card-datapulse","card-olist","btn-linkedin","btn-portfolio","btn-email"]

def src(name):
    return subprocess.check_output(["git","show",f"{BASE}:assets/{name}.svg"], text=True)

def recolor(s, t):
    m = dict(NEUTRAL); m.update({"#D4FF3A": t["A"], "#3B4714": t["dim"]})
    if "fail" in t: m["#FF5C5C"] = t["fail"]
    return re.sub(r"#[0-9A-Fa-f]{6}\b", lambda x: m.get(x.group(0).upper(), x.group(0)), s)

def grad(id_, t, x1, x2, y1=0, y2=0, user=True):
    u = ' gradientUnits="userSpaceOnUse"' if user else ''
    return (f'<linearGradient id="{id_}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{u}>'
            f'<stop offset="0" stop-color="{t["A"]}"/><stop offset="1" stop-color="{t["B"]}"/></linearGradient>')

def header(s, t):
    A, B = t["A"], t["B"]
    ct = dict(A=t.get("C1", A), B=t.get("C2", B))
    defs = (grad("gname", t, 44, 470) + grad("gcells", ct, 744, 920) +
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



# ---------------------------------------------------------------------------
# Tema claro "mp4": branco, tinta preta e o vermelho Marlboro só nos detalhes.
# Precisão = régua milimetrada, células em grafite; velocidade = marcador que
# varre a régua. Uso: python3 scripts/theme.py mp4 assets
RED, INK, TINT = "#E4002B", "#111114", "#FDE8EC"
LIGHT = {"#0A0A0B": "#FFFFFF", "#111113": "#FAFAF8", "#232327": "#E8E8E4", "#34343A": "#D4D4CF",
         "#56565C": "#9C9CA3", "#8C8C93": "#6A6A72", "#F4F4F2": INK, "#D4FF3A": RED,
         "#3B4714": TINT, "#FF5C5C": RED, "#FFB547": "#F2A900",
         "#241A08": "#FFF7E6", "#5A4214": "#F1D9A6"}

def light_recolor(s):
    return re.sub(r"#[0-9A-Fa-f]{6}\b", lambda x: LIGHT.get(x.group(0).upper(), x.group(0)), s)

def light_header(s):
    # antes do recolor: células ok viram grafite, ponto do grid mais suave
    s = s.replace('fill="#D4FF3A" opacity=".92"', f'fill="{INK}" opacity=".9"')
    s = re.sub(r'(\d\d%,90%\{fill:)#D4FF3A', rf'\g<1>{INK}', s)
    s = s.replace('<rect x="636" y="360" width="10" height="10" rx="2" fill="#D4FF3A"/>', f'<rect x="636" y="360" width="10" height="10" rx="2" fill="{INK}"/>')
    s = s.replace('<circle cx="1" cy="1" r="1" fill="#34343A"/>', '<circle cx="1" cy="1" r="1" fill="#E3E3DE"/>')
    s = re.sub(r'<circle cx="790" cy="230" r="260" fill="url\(#glow\)"/>', '', s)
    s = light_recolor(s)
    defs = ('<filter id="sh" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="10" stdDeviation="14" flood-color="#111114" flood-opacity=".08"/></filter>'
            f'<linearGradient id="trail" x1="0" x2="1"><stop offset="0" stop-color="{RED}" stop-opacity="0"/><stop offset="1" stop-color="{RED}" stop-opacity=".45"/></linearGradient>')
    s = s.replace("<defs>", "<defs>" + defs, 1)
    s = s.replace("</style>", ".sw{animation:sw 7s cubic-bezier(.7,0,.2,1) infinite}@keyframes sw{0%{transform:translateX(0)}55%,100%{transform:translateX(904px)}}</style>", 1)
    s = s.replace('<rect x="616" y="96" width="336" height="300" rx="14"', '<rect x="616" y="96" width="336" height="300" rx="14" filter="url(#sh)"', 1)
    ticks = "".join(f'<line x1="{x}" y1="{452 - (8 if (x-48) % 80 == 0 else 4)}" x2="{x}" y2="452" stroke="{"#BDBDB7" if (x-48) % 80 == 0 else "#DEDED9"}"/>' for x in range(48, 953, 8))
    ruler = (f'<g>{ticks}<g class="sw"><rect x="-72" y="446" width="72" height="2" fill="url(#trail)"/>'
             f'<rect x="-1" y="440" width="2" height="12" fill="{RED}"/></g></g>')
    return s.replace("</svg>", ruler + "</svg>")

def light_card(s, name):
    if name == "card-olist":
        s = re.sub(r'(r="9" fill=")#D4FF3A(")', rf'\g<1>{INK}\2', s)
        s = s.replace('fill="#0A0A0B" text-anchor="middle">', 'fill="#FFFFFF" text-anchor="middle">')
    if name == "card-enduro":
        s = s.replace('stroke="#D4FF3A" stroke-width="2"', f'stroke="{INK}" stroke-width="2"')
    s = light_recolor(s)
    s = s.replace('fill="#FAFAF8" stroke="#E8E8E4"/>', 'fill="#FFFFFF" stroke="#E8E8E4"/>', 1)
    # número do card em vermelho, com um traço fino antes (marcação de cronometragem)
    s = re.sub(r'<text x="28" y="42" class="m4" font-size="12" fill="#6A6A72">(\d\d)</text>',
               rf'<rect x="28" y="33" width="2" height="11" fill="{RED}"/><text x="36" y="42" class="m5" font-size="12" fill="{RED}">\1</text>', s)
    return s

def build_light(outdir):
    out = pathlib.Path(outdir)
    for n in FILES:
        s = src(n)
        if n == "header": s = light_header(s)
        elif n.startswith("card"): s = light_card(s, n)
        elif n == "btn-linkedin":
            s = light_recolor(s.replace('fill="#0A0A0B"', 'fill="#FFFFFF"'))
        else:
            s = light_recolor(s).replace('fill="#FAFAF8" stroke="#D4D4CF"', 'fill="#FFFFFF" stroke="#D4D4CF"')
        (out / f"{n}.svg").write_text(s)


# ---------------------------------------------------------------------------
# Tema "rosso": header grafite com uma faixa diagonal em vermelho Marlboro e painel
# branco por cima (as duas cores da MP4/4, sem gritar), cards em grafite neutro com detalhes vermelhos.
# Uso: python3 scripts/theme.py rosso assets
MRED, DRED = "#E4002B", "#B5001F"
DARK_RED = "#FF2D4F"   # vermelho um pouco mais claro para texto pequeno sobre grafite
W = lambda o: f'#FFFFFF" fill-opacity="{o}'

def rosso_header(s):
    s = s.replace('<rect x=".5" y=".5" width="999" height="459" rx="20" fill="#0A0A0B" stroke="#232327"/>',
                  f'<rect x=".5" y=".5" width="999" height="459" rx="20" fill="#121214" stroke="#26262A"/>'
                  '<g clip-path="url(#clip)"><polygon points="720,0 1000,0 1000,460 590,460" fill="url(#slab)"/>'
                  '<line x1="720" y1="0" x2="590" y2="460" stroke="#E4002B" stroke-opacity=".7"/></g>')
    s = s.replace('<circle cx="1" cy="1" r="1" fill="#34343A"/>', '<circle cx="1" cy="1" r="1" fill="#FFFFFF" fill-opacity=".14"/>')
    s = s.replace('fill="#8C8C93">cavalchi', f'fill="{W(.72)}">cavalchi')
    s = s.replace('<circle class="pulse" cx="751" cy="54" r="4" fill="#D4FF3A"/>', f'<circle class="pulse" cx="751" cy="54" r="4" fill="{MRED}"/>')
    s = s.replace('fill="#F4F4F2" text-anchor="end">aberto', 'fill="#FFFFFE" text-anchor="end">aberto')
    s = re.sub(r'(<text x="44" y="(186|288)"[^>]*fill=")#F4F4F2', r'\1#FFFFFE', s)
    s = re.sub(r'Cavalchi<tspan class="g6" fill="#D4FF3A">', f'Cavalchi<tspan class="g6" fill="{MRED}">', s)
    s = s.replace('<text x="48" y="352" class="g4" font-size="22" fill="#F4F4F2">', '<text x="48" y="352" class="g4" font-size="22" fill="#FFFFFE">')
    s = s.replace('<text x="48" y="382" class="g4" font-size="22" fill="#8C8C93">', f'<text x="48" y="382" class="g4" font-size="22" fill="{W(.78)}">')
    s = s.replace('<text x="48" y="424" class="m4" font-size="13" fill="#56565C">', f'<text x="48" y="424" class="m4" font-size="13" fill="{W(.62)}">')
    s = re.sub(r'<circle cx="790" cy="230" r="260" fill="url\(#glow\)"/>', '', s)
    # painel branco: células ok em grafite
    s = s.replace('fill="#D4FF3A" opacity=".92"', f'fill="{INK}" opacity=".9"')
    s = re.sub(r'(\d\d%,90%\{fill:)#D4FF3A', rf'\g<1>{INK}', s)
    s = s.replace('<rect x="636" y="360" width="10" height="10" rx="2" fill="#D4FF3A"/>', f'<rect x="636" y="360" width="10" height="10" rx="2" fill="{INK}"/>')
    s = light_recolor(s)
    s = s.replace('<rect x="616" y="96" width="336" height="300" rx="14" fill="#FAFAF8" stroke="#E8E8E4"/>',
                  '<rect x="616" y="96" width="336" height="300" rx="14" fill="#FFFFFF" filter="url(#sh)"/>')
    defs = ('<clipPath id="clip"><rect width="1000" height="460" rx="20"/></clipPath>'
            f'<linearGradient id="slab" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{MRED}" stop-opacity=".22"/><stop offset=".5" stop-color="{MRED}" stop-opacity=".08"/><stop offset="1" stop-color="{MRED}" stop-opacity=".0"/></linearGradient>'
            '<filter id="sh" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="18" stdDeviation="18" flood-color="#000000" flood-opacity=".55"/></filter>'
            f'<linearGradient id="trail" x1="0" x2="1"><stop offset="0" stop-color="{MRED}" stop-opacity="0"/><stop offset="1" stop-color="{MRED}" stop-opacity=".8"/></linearGradient>')
    s = s.replace("<defs>", "<defs>" + defs, 1)
    s = s.replace("</style>", ".sw{animation:sw 7s cubic-bezier(.7,0,.2,1) infinite}@keyframes sw{0%{transform:translateX(0)}55%,100%{transform:translateX(904px)}}</style>", 1)
    ticks = "".join(f'<line x1="{x}" y1="{452 - (8 if (x-48) % 80 == 0 else 4)}" x2="{x}" y2="452" stroke="#FFFFFF" stroke-opacity="{.35 if (x-48) % 80 == 0 else .14}"/>' for x in range(48, 953, 8))
    return s.replace("</svg>", f'<g>{ticks}<g class="sw"><rect x="-72" y="446" width="72" height="2" fill="url(#trail)"/><rect x="-1" y="440" width="2" height="12" fill="{MRED}"/></g></g></svg>')

DARK = {"#0A0A0B": "#0B0B0D", "#111113": "#131315", "#232327": "#26262A", "#34343A": "#36363C",
        "#56565C": "#5C5C63", "#8C8C93": "#8F8F96", "#F4F4F2": "#F4F4F2", "#D4FF3A": DARK_RED,
        "#3B4714": "#3A0B15", "#FF5C5C": DARK_RED}

def rosso_card(s, name):
    if name == "card-olist":
        s = re.sub(r'(r="9" fill=")#D4FF3A(")', rf'\g<1>{MRED}\2', s)
        s = s.replace('fill="#0A0A0B" text-anchor="middle">', 'fill="#FFFFFF" text-anchor="middle">')
    if name == "card-enduro":
        s = s.replace('stroke="#D4FF3A" stroke-width="2"', 'stroke="#F4F4F2" stroke-width="2"')
    s = re.sub(r"#[0-9A-Fa-f]{6}\b", lambda x: DARK.get(x.group(0).upper(), x.group(0)), s)
    s = re.sub(r'<text x="28" y="42" class="m4" font-size="12" fill="#8F8F96">(\d\d)</text>',
               rf'<rect x="28" y="33" width="2" height="11" fill="{DARK_RED}"/><text x="36" y="42" class="m5" font-size="12" fill="{DARK_RED}">\1</text>', s)
    # vermelho sólido escorrendo pela borda de cima, bem fino
    s = s.replace('stroke="#26262A"/>', 'stroke="#26262A"/><path d="M18 .75 H140" stroke="url(#edge)" stroke-width="1.5"/>'
                  f'<defs><linearGradient id="edge" x1="18" x2="140" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{MRED}"/><stop offset="1" stop-color="{MRED}" stop-opacity="0"/></linearGradient></defs>', 1)
    return s

def build_rosso(outdir):
    out = pathlib.Path(outdir)
    for n in FILES:
        s = src(n)
        if n == "header": s = rosso_header(s)
        elif n.startswith("card"): s = rosso_card(s, n)
        elif n == "btn-linkedin":
            s = s.replace('fill="#D4FF3A" stroke="#D4FF3A"', f'fill="{MRED}" stroke="{MRED}"').replace('fill="#0A0A0B"', 'fill="#FFFFFF"')
        else:
            s = re.sub(r"#[0-9A-Fa-f]{6}\b", lambda x: DARK.get(x.group(0).upper(), x.group(0)), s)
        (out / f"{n}.svg").write_text(s)

if __name__ == "__main__":
    {"mp4": build_light, "rosso": build_rosso}.get(sys.argv[1], lambda o: build(sys.argv[1], o))(sys.argv[2])
