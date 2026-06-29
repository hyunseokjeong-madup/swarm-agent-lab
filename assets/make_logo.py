"""Generate a pixel-art logo (assets/logo.svg) for MADOBI. Pure stdlib."""
from pathlib import Path

S = 16  # pixel size
FONT = {  # 5x7 bitmaps
"M":["10001","11011","10101","10101","10001","10001","10001"],
"A":["01110","10001","10001","11111","10001","10001","10001"],
"D":["11110","10001","10001","10001","10001","10001","11110"],
"O":["01110","10001","10001","10001","10001","10001","01110"],
"B":["11110","10001","10001","11110","10001","10001","11110"],
"I":["11111","00100","00100","00100","00100","00100","11111"],
}
WORD = "MADOBI"

# pixel robot mark (9x9): B body, E eye, A antenna, M mouth
ROBOT = [
"....A....",
"....A....",
".BBBBBBB.",
".B.....B.",
".B.E.E.B.",
".B.....B.",
".B.MMM.B.",
".BBBBBBB.",
"..B...B..",
]
MARKCOL = {"B":"#7c83ff","E":"#6ee7ff","A":"#b072ff","M":"#b072ff"}

def lerp(a,b,t): return tuple(round(a[i]+(b[i]-a[i])*t) for i in range(3))
def hexs(c): return "#%02x%02x%02x"%c
CYAN=(110,231,255); PUR=(176,114,255)

rects=[]
# --- mark ---
mx,my=46,52
for r,row in enumerate(ROBOT):
    for c,ch in enumerate(row):
        if ch!=".":
            rects.append(f'<rect x="{mx+c*S}" y="{my+r*S}" width="{S-1}" height="{S-1}" rx="2" fill="{MARKCOL[ch]}"/>')

# --- wordmark MADOBI ---
wx,wy=232,78
tot=len(WORD)*5
col=0
for li,ch in enumerate(WORD):
    bm=FONT[ch]
    for r in range(7):
        for c in range(5):
            if bm[r][c]=="1":
                t=(li*5+c)/tot
                fill=hexs(lerp(CYAN,PUR,t))
                x=wx+(li*6+c)*S; y=wy+r*S
                rects.append(f'<rect x="{x}" y="{y}" width="{S-1}" height="{S-1}" rx="2" fill="{fill}"/>')

W,H=232+len(WORD)*6*S+40, 260
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="'Courier New',monospace">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b1020"/><stop offset="1" stop-color="#161d3a"/></linearGradient>
  </defs>
  <rect x="0" y="0" width="{W}" height="{H}" rx="24" fill="url(#bg)"/>
  <!-- faint pixel grid -->
  <g opacity="0.06" stroke="#9fb0d9" stroke-width="1">
  {''.join(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}"/>' for y in range(0,H,S))}
  {''.join(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}"/>' for x in range(0,W,S))}
  </g>
  {''.join(rects)}
  <text x="234" y="230" font-size="19" font-weight="700" fill="#9fb0d9" font-family="'Courier New',monospace">swarm-optimized marketing agent · 정합성 보장 · never wrong with numbers</text>
</svg>
'''
out=Path(__file__).parent/"logo.svg"
out.write_text(svg,encoding="utf-8")
print("wrote",out,f"({W}x{H})")
