"""Gera assets/datalake.svg: o pescador de dados, no estilo dos cards (grafite + vermelho Marlboro).
Uso: python3 scripts/datalake.py assets/datalake.svg
"""
import re, subprocess, sys

RED, INK, BG, LINE, MUTED, DIM, TXT = "#E4002B", "#0B0B0D", "#131315", "#26262A", "#8F8F96", "#5C5C63", "#F4F4F2"
W, H, SURF = 1000, 410, 232   # largura, altura, linha d'água

def fonts():
    css = subprocess.check_output(["git", "show", "06118db:assets/card-finsight.svg"], text=True)
    css = re.search(r"<style>(.*?)</style>", css, re.S).group(1)
    return "".join(re.findall(r"@font-face\{[^}]*\}", css)) + "".join(re.findall(r"\.[gm]\d\{[^}]*\}", css))

def fish(label, w, color="#1D1D21", stroke="#3A3A41", txt=MUTED, facing=1):
    """peixe estilizado centrado em 0,0; facing=1 nada para a direita."""
    h = 22
    body = (f'<path d="M{-w/2} 0 C{-w/2+10} {-h/2-2} {w/2-14} {-h/2} {w/2} 0 C{w/2-14} {h/2} {-w/2+10} {h/2+2} {-w/2} 0 Z" fill="{color}" stroke="{stroke}"/>'
            f'<path d="M{-w/2+2} 0 L{-w/2-12} -10 L{-w/2-8} 0 L{-w/2-12} 10 Z" fill="{color}" stroke="{stroke}" stroke-linejoin="round"/>'
            f'<circle cx="{w/2-9}" cy="-2" r="1.6" fill="{txt}"/>')
    t = f'<text x="{-3}" y="3.5" class="m4" font-size="10" fill="{txt}" text-anchor="middle">{label}</text>'
    if facing == 1:
        return body + t
    return f'<g transform="scale(-1,1)">{body}</g>' + t.replace(f'x="{-3}"', 'x="3"')

def swimmer(label, w, y, dur, delay, facing):
    x0, x1 = (-80, W + 80) if facing == 1 else (W + 80, -80)
    return (f'<g transform="translate({x0},{y})"><animateTransform attributeName="transform" type="translate" '
            f'values="{x0},{y};{(x0+x1)/2},{y+5};{x1},{y}" dur="{dur}s" begin="-{delay}s" repeatCount="indefinite"/>'
            f'<g class="wig">{fish(label, w, facing=facing)}</g></g>')


# ---------------------------------------------------------------------------
# A pescaria, calculada quadro a quadro para tudo ficar preso no lugar:
# o peixe nada até a boia, morde, o pescador fisga, gira a vara por cima da
# cabeça, solta o peixe no balde e lança a boia de volta.
import math
T, N = 10.0, 250                      # duração do ciclo (s) e quadros amostrados
PIV, R = (294.0, 182.0), 172.0        # mãos (pivô da vara) e comprimento da vara
BASE = -35.0                          # ângulo da vara em repouso (graus, negativo = pra cima)
WATER_B = (505.0, SURF - 2.0)         # boia na água
HOOK_DROP = 22.0                      # anzol fica 22px abaixo da boia
BASKET = (154.0, SURF - 30.0)         # centro da boca do balde (x) e fundo (y)
T_ARRIVE, T_BITE, T_STRIKE, T_SWING, T_LOWER, T_DROP, T_CAST, T_RELEASE, T_LAND = 2.4, 2.7, 3.2, 3.8, 4.8, 5.4, 6.0, 6.5, 7.25

def ease(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def ein(x): x = max(0.0, min(1.0, x)); return x ** 3
def lerp(a, b, k): return a + (b - a) * k
def seg(t, a, b): return (t - a) / (b - a)

def angle(t):
    if t < T_BITE: return BASE + math.sin(t * 2.2) * 0.8
    if t < T_STRIKE: return BASE + 3.5 * abs(math.sin((t - T_BITE) * 2 * math.pi / 0.25))  # ponta treme na mordida
    if t < T_SWING: return lerp(BASE, -58, 1 - (1 - seg(t, T_STRIKE, T_SWING)) ** 3)       # fisgada: puxão seco
    if t < T_LOWER: return lerp(-58, -72, ease(seg(t, T_SWING, T_LOWER)))                  # traz o peixe para o balde
    if t < T_CAST: return -72 + math.sin((t - T_LOWER) * 6) * 1.2
    if t < T_CAST + 0.3: return lerp(-72, -112, ease(seg(t, T_CAST, T_CAST + 0.3)))        # arma o lançamento
    if t < T_RELEASE + 0.12: return lerp(-112, -16, ein(seg(t, T_CAST + 0.3, T_RELEASE + 0.12)) ** 0.7)
    return lerp(-16, BASE, ease(seg(t, T_RELEASE + 0.12, T_LAND + 0.5)))

def tip(t):
    a = math.radians(angle(t)); return (PIV[0] + R * math.cos(a), PIV[1] + R * math.sin(a))

def line_len(t):
    if t < T_LOWER: return 62.0
    if t < T_DROP: return lerp(62, 128, ease(seg(t, T_LOWER, T_DROP)))   # desce o peixe dentro do balde
    return lerp(128, 30, ease(seg(t, T_DROP, T_CAST)))                   # recolhe a linha

def hang(t):
    tp = tip(max(0.0, t - 0.12))           # o peixe pendurado atrasa um pouco (pêndulo)
    return (tp[0], tip(t)[1] + line_len(t))

def hook(t):
    """posição do anzol (boca do peixe quando fisgado)."""
    wh = (WATER_B[0], WATER_B[1] + HOOK_DROP)
    if t < T_STRIKE: return wh
    if t < T_STRIKE + 0.45: 
        k = ease(seg(t, T_STRIKE, T_STRIKE + 0.45)); h = hang(t); return (lerp(wh[0], h[0], k), lerp(wh[1], h[1], k))
    if t < T_RELEASE: return hang(t)
    b = bobber(t); return (b[0], b[1] + HOOK_DROP * (0.4 if t < T_LAND else 1))

def bobber(t):
    if t < T_BITE: return (WATER_B[0], WATER_B[1] + math.sin(t * 3.1) * 1.2)
    if t < T_STRIKE: return (WATER_B[0], WATER_B[1] + 7 * abs(math.sin((t - T_BITE) * 2 * math.pi / 0.25)))
    if t < T_RELEASE:
        h = hook(t); tp = tip(t); d = math.dist(h, tp) or 1
        k = min(HOOK_DROP, d - 4) / d; return (h[0] + (tp[0] - h[0]) * k, h[1] + (tp[1] - h[1]) * k)
    if t < T_LAND:                       # voo da boia em parábola até a água
        k = seg(t, T_RELEASE, T_LAND); p0 = bobber_release
        x = lerp(p0[0], WATER_B[0], k); y = lerp(p0[1], WATER_B[1], k) - 150 * k * (1 - k)
        return (x, y)
    s_ = t - T_LAND; return (WATER_B[0], WATER_B[1] + 5 * math.exp(-s_ * 3) * math.cos(s_ * 9) + math.sin(t * 3.1) * 1.2)

def _release_point():
    global bobber_release
    bobber_release = (0, 0)
    t = T_RELEASE - 1e-3; h = hang(t); tp = tip(t); d = math.dist(h, tp)
    k = min(HOOK_DROP, d - 4) / d
    bobber_release = (h[0] + (tp[0] - h[0]) * k, h[1] + (tp[1] - h[1]) * k)

def fish_pose(t):
    """(x, y, rotação, opacidade) do peixe: o desenho tem a boca na origem e o corpo para +x."""
    if t < T_ARRIVE:
        k = ease(seg(t, 0, T_ARRIVE)) ** 0.85
        x = lerp(W + 70, WATER_B[0] + 8, k); y = WATER_B[1] + HOOK_DROP + 14 * (1 - k) + 3 * math.sin(t * 5)
        return x, y, 4 * math.sin(t * 9), 0.6
    if t < T_STRIKE:
        h = hook(t); k = ease(seg(t, T_ARRIVE, T_BITE)); wob = math.sin(t * 40) * 3 if t > T_BITE else 0
        return lerp(WATER_B[0] + 8, h[0], k), h[1] + wob, 6 * math.sin(t * 30), 0.6
    h = hook(t); rot = lerp(0, 90, ease(seg(t, T_STRIKE, T_STRIKE + 0.4)))
    rot += 12 * math.sin(t * 13) * (1 if t < T_DROP else 0.3)
    op = 1 - ease(seg(t, T_DROP - 0.15, T_DROP + 0.1))
    if h[1] > SURF + 3: op *= 0.6
    return h[0], h[1], rot, op

def fmt(v): return f"{v:.1f}"

def catch_css():
    pc = lambda t: f"{t / T * 100:.2f}%"
    return (f".c0{{animation:c0 {T}s steps(1) infinite}}@keyframes c0{{0%,{pc(T_DROP)}{{opacity:1}}{pc(T_DROP + .01)},100%{{opacity:0}}}}"
            f".c1{{animation:c1 {T}s steps(1) infinite}}@keyframes c1{{0%,{pc(T_DROP)}{{opacity:0}}{pc(T_DROP + .01)},100%{{opacity:1}}}}"
            f".glint{{animation:gl {T}s ease-out infinite}}@keyframes gl{{0%,{pc(T_DROP - .05)}{{opacity:0}}{pc(T_DROP + .05)}{{opacity:1}}{pc(T_DROP + 1.2)},100%{{opacity:0}}}}"
            f".r1{{animation:r1 {T}s ease-out infinite;transform-box:fill-box;transform-origin:center}}@keyframes r1{{0%,{pc(T_BITE)}{{transform:scale(.2);opacity:0}}{pc(T_BITE + .05)}{{opacity:.8}}{pc(T_BITE + 1.4)},100%{{transform:scale(2.6);opacity:0}}}}"
            f".r2{{animation:r2 {T}s ease-out infinite;transform-box:fill-box;transform-origin:center}}@keyframes r2{{0%,{pc(T_STRIKE)}{{transform:scale(.2);opacity:0}}{pc(T_STRIKE + .05)}{{opacity:.9}}{pc(T_STRIKE + 1.2)},100%{{transform:scale(3);opacity:0}}}}"
            f".r3{{animation:r3 {T}s ease-out infinite;transform-box:fill-box;transform-origin:center}}@keyframes r3{{0%,{pc(T_LAND)}{{transform:scale(.2);opacity:0}}{pc(T_LAND + .05)}{{opacity:.9}}{pc(T_LAND + 1.4)},100%{{transform:scale(2.8);opacity:0}}}}")

def catch_scene():
    _release_point()
    ts = [i * T / N for i in range(N + 1)]
    kt = ";".join(f"{t / T:.4f}" for t in ts)
    anim = lambda attr, vals: f'<animate attributeName="{attr}" dur="{T}s" repeatCount="indefinite" calcMode="linear" keyTimes="{kt}" values="{";".join(vals)}"/>'
    def at(kind, vals): return f'<animateTransform attributeName="transform" type="{kind}" dur="{T}s" repeatCount="indefinite" calcMode="linear" keyTimes="{kt}" values="{";".join(vals)}"/>'
    rod_d, line_d, bob_v, fish_t, fish_r, fish_o = [], [], [], [], [], []
    for t in ts:
        a = math.radians(angle(t)); u = (math.cos(a), math.sin(a)); tp = tip(t)
        loaded = T_STRIKE <= t < T_DROP
        bend = 16 if loaded else 5
        perp = (math.sin(a), -math.cos(a))
        if perp[1] > 0: perp = (-perp[0], -perp[1])
        if loaded: perp = (-perp[0], -perp[1]) if False else perp
        butt = (PIV[0] - 16 * u[0], PIV[1] - 16 * u[1])
        c = (PIV[0] + .55 * R * u[0] + perp[0] * bend * (-1 if loaded else 1), PIV[1] + .55 * R * u[1] + perp[1] * bend * (-1 if loaded else 1))
        rod_d.append(f"M{fmt(butt[0])} {fmt(butt[1])} Q{fmt(c[0])} {fmt(c[1])} {fmt(tp[0])} {fmt(tp[1])}")
        b = bobber(t); h = hook(t)
        end = b if (t < T_STRIKE or t >= T_RELEASE) else h
        sag = 3 if loaded else (22 if T_RELEASE <= t < T_LAND else 10)
        m = ((tp[0] + end[0]) / 2, (tp[1] + end[1]) / 2 + sag)
        line_d.append(f"M{fmt(tp[0])} {fmt(tp[1])} Q{fmt(m[0])} {fmt(m[1])} {fmt(end[0])} {fmt(end[1])}")
        bob_v.append(f"{fmt(b[0])},{fmt(b[1])}")
        fx, fy, fr, fo = fish_pose(t)
        fish_t.append(f"{fmt(fx)},{fmt(fy)}"); fish_r.append(fmt(fr)); fish_o.append(f"{fo:.2f}")
    fw = 50
    body = (f'<path d="M0 0 C6 -12 {fw-18} -11 {fw-6} 0 C{fw-18} 11 6 12 0 0 Z" fill="#ECECEF"/>'
            f'<path d="M{fw-8} 0 L{fw+6} -9 L{fw+3} 0 L{fw+6} 9 Z" fill="#ECECEF"/>'
            f'<circle cx="8" cy="-2.5" r="1.6" fill="{INK}"/>'
            f'<text x="{fw/2+1}" y="3.5" class="m5" font-size="9.5" fill="{INK}" text-anchor="middle">csv</text>')
    bx, by = 325, SURF - 30
    out = [
        f'<ellipse class="r1" cx="{WATER_B[0]}" cy="{SURF}" rx="12" ry="2.5" fill="none" stroke="{MUTED}"/>',
        f'<ellipse class="r2" cx="{WATER_B[0]}" cy="{SURF}" rx="14" ry="3" fill="none" stroke="{TXT}"/>',
        f'<ellipse class="r3" cx="{WATER_B[0]}" cy="{SURF}" rx="12" ry="2.5" fill="none" stroke="{MUTED}"/>',
        # peixe (atrás da linha e da boia)
        f'<g>{at("translate", fish_t)}<g>{at("rotate", fish_r)}<g>{anim("opacity", fish_o)}{body}</g></g></g>',
        # braço segue o pivô, vara e linha
        f'<path d="M272 {SURF-74} L{PIV[0]-6} {PIV[1]-6} L{PIV[0]} {PIV[1]}" fill="none" stroke="#D9D9DD" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>',
        f'<path d="{line_d[0]}" fill="none" stroke="{MUTED}" stroke-width=".9">{anim("d", line_d)}</path>',
        f'<path d="{rod_d[0]}" fill="none" stroke="#7A7A83" stroke-width="2.6" stroke-linecap="round">{anim("d", rod_d)}</path>',
        f'<circle cx="{PIV[0]+4}" cy="{PIV[1]-3}" r="3.5" fill="#2A2A30" stroke="#7A7A83"/>',
        f'<g>{at("translate", bob_v)}<circle r="5.5" fill="{TXT}"/><path d="M-5.5 0 A5.5 5.5 0 0 1 5.5 0 Z" fill="{RED}"/></g>',
        # balde na frente: o peixe some dentro dele
        f'<path d="M{bx} {by-38} L{bx+44} {by-38} L{bx+39} {by} L{bx+5} {by} Z" fill="#232328" stroke="#3A3A41"/>',
        f'<path d="M{bx+3} {by-38} Q{bx+22} {by-62} {bx+41} {by-38}" fill="none" stroke="#3A3A41" stroke-width="1.5"/>',
        f'<text x="{bx+22}" y="{by-15}" class="m5" font-size="10" fill="{TXT}" text-anchor="middle">ETL</text>',
        f'<rect class="glint" x="{bx-2}" y="{by-40}" width="48" height="42" rx="3" fill="none" stroke="{RED}"/>',
    ]
    return "".join(out)

def build():
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
         'aria-label="Um pescador sentado no píer pesca arquivos de dados no data lake e guarda no balde de ETL">']
    s.append("<style>" + fonts() +
             ".wig{animation:wig .9s ease-in-out infinite alternate}@keyframes wig{to{transform:skewY(4deg)}}"
             ".cur{animation:cur 3s linear infinite}@keyframes cur{to{stroke-dashoffset:-40}}"
             ".tw{animation:tw 3s ease-in-out infinite}@keyframes tw{50%{opacity:.15}}"
             + catch_css() + "</style>")
    s.append(f'<defs><clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>'
             f'<linearGradient id="water" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#18181C"/><stop offset="1" stop-color="#0C0C0E"/></linearGradient>'
             f'<linearGradient id="edge" x1="18" x2="160" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{RED}"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></linearGradient>'
             f'<linearGradient id="haze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{RED}" stop-opacity="0"/><stop offset="1" stop-color="{RED}" stop-opacity=".07"/></linearGradient>'
             '<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#2A2A30"/></pattern></defs>')
    s.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="18" fill="{BG}" stroke="{LINE}"/>'
             f'<path d="M18 .75 H160" stroke="url(#edge)" stroke-width="1.5"/><g clip-path="url(#card)">')
    # céu: grade de pontos, lua fininha, estrelas
    s.append(f'<rect width="{W}" height="{SURF}" fill="url(#dots)" opacity=".7"/><rect y="120" width="{W}" height="{SURF-120}" fill="url(#haze)"/>')
    s.append(f'<circle cx="880" cy="96" r="18" fill="{TXT}" opacity=".9"/><circle cx="888" cy="90" r="17" fill="{BG}"/>')
    for i, (x, y) in enumerate([(560, 70), (640, 120), (720, 64), (790, 150), (940, 160), (470, 110), (980, 60)]):
        s.append(f'<circle class="tw" style="animation-delay:{i*.45:.2f}s" cx="{x}" cy="{y}" r="1.3" fill="{TXT}"/>')
    # cabeçalho no estilo dos cards
    s.append(f'<rect x="28" y="33" width="2" height="11" fill="{RED}"/><text x="36" y="42" class="m5" font-size="12" fill="{RED}">05</text>'
             f'<text x="60" y="42" class="m4" font-size="12" fill="{MUTED}">data lake</text>'
             f'<text x="{W-28}" y="42" class="m4" font-size="11" fill="{MUTED}" text-anchor="end" letter-spacing="0.5">TURNO DA MADRUGADA</text>')
    # água
    s.append(f'<rect y="{SURF}" width="{W}" height="{H-SURF}" fill="url(#water)"/>'
             f'<line x1="0" y1="{SURF}" x2="{W}" y2="{SURF}" stroke="#3A3A41"/>')
    for i, y in enumerate([250, 280, 310, 342]):
        s.append(f'<line class="cur" style="animation-duration:{3+i*1.4:.1f}s" x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="#202025" stroke-dasharray="{14+i*6} {26+i*10}"/>')
    # régua de profundidade = camadas do lake
    for y in range(SURF + 8, H - 50, 6):
        major = (y - SURF) % 36 == 0
        s.append(f'<line x1="{W-30}" y1="{y}" x2="{W-30+(9 if major else 4)}" y2="{y}" stroke="#3A3A41" stroke-opacity="{1 if major else .6}"/>')
    for y, t in [(SURF + 36, "raw"), (SURF + 72, "staging"), (SURF + 108, "marts")]:
        s.append(f'<text x="{W-38}" y="{y+3}" class="m4" font-size="10" fill="{DIM}" text-anchor="end">{t}</text>')
    # píer
    s.append(f'<rect x="20" y="{SURF-30}" width="410" height="9" rx="2" fill="#2A2A30"/>'
             f'<line x1="20" y1="{SURF-26}" x2="430" y2="{SURF-26}" stroke="#1E1E22"/>')
    for x in (52, 150, 250, 340, 416):
        s.append(f'<rect x="{x}" y="{SURF-21}" width="7" height="{H-SURF-25}" fill="#1F1F23"/>')
    # peixes (mais fundo = mais refinado)
    for args in [("tsv", 56, 254, 15, 9, -1), ("json", 64, 274, 19, 3, 1), ("api", 54, 296, 23, 4, -1),
                 ("log", 52, 316, 17, 12, 1), ("xlsx", 60, 334, 27, 20, -1), ("parquet", 88, 352, 31, 6, 1)]:
        s.append(swimmer(*args))
    # pescador sentado na beira do píer (boné vermelho, a única peça de cor)
    s.append('<g>'
             f'<path d="M268 {SURF-30} L292 {SURF-30} L296 {SURF-6} L304 {SURF+2}" fill="none" stroke="#3B3B44" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>'
             f'<path d="M300 {SURF+2} L310 {SURF+2}" stroke="{TXT}" stroke-width="5" stroke-linecap="round"/>'
             f'<path d="M264 {SURF-32} C258 {SURF-60} 262 {SURF-78} 270 {SURF-86}" fill="none" stroke="{TXT}" stroke-width="20" stroke-linecap="round"/>'
             f'<circle cx="274" cy="{SURF-104}" r="11" fill="#C9A88A"/>'
             f'<path d="M262 {SURF-106} Q263 {SURF-121} 276 {SURF-120} Q287 {SURF-119} 286 {SURF-108} Z" fill="{RED}"/>'
             f'<path d="M284 {SURF-108} L296 {SURF-106}" stroke="{RED}" stroke-width="3" stroke-linecap="round"/>'
             '</g>')
    s.append(catch_scene())
    # rodapé: contador e telemetria
    s.append(f'<rect x="0" y="{H-46}" width="{W}" height="46" fill="#0C0C0E" opacity=".72"/>'
             f'<line x1="0" y1="{H-46}" x2="{W}" y2="{H-46}" stroke="{LINE}"/>'
             f'<text x="28" y="{H-19}" class="m5" font-size="12" fill="{RED}">›</text>'
             f'<text x="44" y="{H-19}" class="m4" font-size="12" fill="{TXT}"><tspan class="c0">2.417</tspan></text>'
             f'<text x="44" y="{H-19}" class="m4" font-size="12" fill="{TXT}"><tspan class="c1">2.418</tspan></text>'
             f'<text x="90" y="{H-19}" class="m4" font-size="12" fill="{MUTED}">registros pescados  ·  0 nulos  ·  schema ok</text>'
             f'<text x="{W-28}" y="{H-19}" class="m4" font-size="11" fill="{DIM}" text-anchor="end">// pescando insight no data lake</text>'
             )
    s.append("</g></svg>")
    return "".join(s)

if __name__ == "__main__":
    open(sys.argv[1] if len(sys.argv) > 1 else "assets/datalake.svg", "w").write(build())
