# Diagram helpers (SVG -> PNG via headless Chrome) for the deck architecture figures.
import base64, html, os, subprocess, io
from PIL import Image
TH=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'assets', 'img') + '/'
FAM={ # fill, stroke, text
 'data':('#F1F3F6','#7D8796'),'frozen':('#DCEAFE','#2F6FD0'),'train':('#FFE9D2','#D9822B'),
 'classic':('#DDF2E3','#2E9457'),'gate':('#FBE0E0','#C0392B'),'out':('#ECE5FB','#6E4FC2'),
 'human':('#FFF3CF','#B8860B'),'store':('#E6F4F6','#1F8A99'),'neutral':('#FFFFFF','#5B6472'),
 'ghost':('#F7F7F8','#B7BCC5'),
}
INK='#1B2230'; MUTED='#5B6472'
def esc(s): return html.escape(str(s))
import re as _re
def mk(t,size):
    """markup: ^{sup} _{sub} -> tspans with dy shifts"""
    out=[]; pos=0; sm=round(size*0.68,1)
    for m in _re.finditer(r'([\^_])\{([^}]*)\}',t):
        out.append(esc(t[pos:m.start()]))
        d=-0.42*size if m[1]=='^' else 0.26*size
        out.append(f'<tspan dy="{d:.1f}" font-size="{sm}">{esc(m[2])}</tspan><tspan dy="{-d:.1f}">\u200b</tspan>')
        pos=m.end()
    out.append(esc(t[pos:])); return ''.join(out)
_cache={}
def datauri(name, maxw=420):
    if name in _cache: return _cache[name]
    p=name if name.startswith('/') else TH+name+('' if '.' in name else '.jpg')
    im=Image.open(p).convert('RGB'); im.thumbnail((maxw,maxw))
    b=io.BytesIO(); im.save(b,'JPEG',quality=90); u='data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode()
    _cache[name]=u; return u
class Fig:
    def __init__(s,W,H,bg='#FFFFFF'):
        s.W,s.H,s.bg=W,H,bg; s.e=[]
    def add(s,x): s.e.append(x)
    def text(s,x,y,t,size=16,w=400,c=INK,a='start',mono=False,it=False,ser=False,op=1):
        fam="IBM Plex Mono" if mono else ("Noto Serif" if ser else "IBM Plex Sans")
        lines=str(t).split('\n')
        for i,l in enumerate(lines):
            s.add(f'<text x="{x}" y="{y+i*size*1.25}" font-family="{fam}" font-size="{size}" font-weight="{w}" fill="{c}" text-anchor="{a}"{" font-style=\"italic\"" if it else ""} opacity="{op}">{mk(l,size)}</text>')
    def rect(s,x,y,w,h,fill='#fff',stroke='#000',sw=1.5,rx=8,dash=False,op=1):
        s.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{" stroke-dasharray=\"7 5\"" if dash else ""} fill-opacity="{op}"/>')
    def box(s,x,y,w,h,fam,title,lines=(),num=None,tag=None,dash=False,ts=18,ls=15,mono_lines=True,center=False,rx=8):
        f,k=FAM[fam]; s.rect(x,y,w,h,f,k,1.8,rx,dash)
        cx=x+w/2 if center else x+12; a='middle' if center else 'start'
        ty=y+ts+8
        s.text(cx,ty,title,ts,600,INK,a)
        yy=ty+ts*0.35+ls*1.15*len(str(title).split('\n'))-ls*0.1
        for l in lines:
            m = mono_lines and not str(l).startswith('~')
            s.text(cx,yy,str(l).lstrip('~'),ls,400,'#2A3242' if m else MUTED,a,mono=m); yy+=ls*1.32
        if num is not None: s.num(x-2,y-2,num)
        if tag: s.tag(x+w-8,y-10,tag,k)
    def tag(s,xr,y,t,color):
        w=len(t)*7.6+14; s.add(f'<rect x="{xr-w}" y="{y}" width="{w}" height="20" rx="10" fill="#fff" stroke="{color}" stroke-width="1.4"/>')
        s.text(xr-w/2,y+14.5,t,12.5,600,color,'middle')
    def num(s,x,y,n,c='#1B2230'):
        s.add(f'<circle cx="{x}" cy="{y}" r="13" fill="{c}"/>'); s.text(x,y+5.5,n,15,700,'#fff','middle')
    def arrow(s,pts,c='#2B2F36',w=1.8,dash=False,head=True,label=None,lx=None,ly=None,lsize=14,lc=None,la='middle',mono=True):
        d='M '+' L '.join(f'{p[0]} {p[1]}' for p in pts)
        mid=f'url(#ah{c.strip("#")})'
        s.markers.add(c) if hasattr(s,'markers') else setattr(s,'markers',{c})
        s.add(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w}"{" stroke-dasharray=\"6 5\"" if dash else ""}{f" marker-end=\"{mid}\"" if head else ""}/>')
        if label:
            if lx is None: lx=(pts[0][0]+pts[-1][0])/2; ly=(pts[0][1]+pts[-1][1])/2-7
            s.text(lx,ly,label,lsize,500,lc or '#3A4456',la,mono=mono)
    def curve(s,d,c='#2B2F36',w=1.8,dash=False,head=True):
        s.markers.add(c) if hasattr(s,'markers') else setattr(s,'markers',{c})
        s.add(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w}"{" stroke-dasharray=\"6 5\"" if dash else ""}{f" marker-end=\"url(#ah{c.strip(chr(35))})\"" if head else ""}/>')
    def img(s,x,y,w,h,name,stroke='#3A4456',sw=1.2,op=1,grey=False):
        u=datauri(name)
        s.add(f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="{u}" preserveAspectRatio="xMidYMid slice" opacity="{op}"{" filter=\"url(#grey)\"" if grey else ""}/>')
        s.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{stroke}" stroke-width="{sw}"/>')
    def cross(s,x,y,w,h,c='#C0392B',sw=3):
        s.add(f'<path d="M{x} {y} L{x+w} {y+h} M{x+w} {y} L{x} {y+h}" stroke="{c}" stroke-width="{sw}"/>')
    def thumb(s,x,y,size,name,label=None,sub=None,below=True,grey=False,op=1):
        s.img(x,y,size,size,name,grey=grey,op=op)
        if label and below:
            s.text(x+size/2,y+size+17,label,14.5,600,INK,'middle')
            if sub: s.text(x+size/2,y+size+34,sub,13.5,400,MUTED,'middle',mono=True)
    def stack(s,x,y,size,names,dx=10,dy=-10,label=None,sub=None):
        for i,n in enumerate(reversed(names)):
            k=len(names)-1-i; s.img(x+k*dx,y+k*dy,size,size,n)
        if label: s.text(x+size/2+dx*(len(names)-1)/2,y+size+17,label,14.5,600,INK,'middle')
        if sub: s.text(x+size/2+dx*(len(names)-1)/2,y+size+34,sub,13.5,400,MUTED,'middle',mono=True)
    def cuboid(s,x,y,w,h,d,fam='frozen',label=None,sub=None,ls=13.5):
        f,k=FAM[fam]
        s.add(f'<polygon points="{x},{y} {x+d},{y-d} {x+w+d},{y-d} {x+w},{y}" fill="{k}" fill-opacity="0.35" stroke="{k}" stroke-width="1.3"/>')
        s.add(f'<polygon points="{x+w},{y} {x+w+d},{y-d} {x+w+d},{y+h-d} {x+w},{y+h}" fill="{k}" fill-opacity="0.55" stroke="{k}" stroke-width="1.3"/>')
        s.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{f}" stroke="{k}" stroke-width="1.3"/>')
        if label: s.text(x+w/2+d/2,y+h+16,label,ls,500,'#2A3242','middle',mono=True)
        if sub: s.text(x+w/2+d/2,y+h+32,sub,ls,400,MUTED,'middle',mono=True)
    def tokens(s,x,y,n,c,cell=14,gap=3,masked=(),vertical=False,cls=False):
        for i in range(n):
            xx=x+(0 if vertical else i*(cell+gap)); yy=y+(i*(cell+gap) if vertical else 0)
            if i in masked:
                s.add(f'<rect x="{xx}" y="{yy}" width="{cell}" height="{cell}" fill="#fff" stroke="#9AA1AD" stroke-dasharray="3 2" stroke-width="1"/>')
                s.add(f'<path d="M{xx+2} {yy+2} L{xx+cell-2} {yy+cell-2}" stroke="#9AA1AD" stroke-width="1"/>')
            else:
                s.add(f'<rect x="{xx}" y="{yy}" width="{cell}" height="{cell}" fill="{c}" stroke="#1B2230" stroke-width="0.6"/>')
    def group(s,x,y,w,h,label=None,dash=True,fill='#FAFBFC',stroke='#9AA3B2',lc=MUTED,ls=14):
        s.rect(x,y,w,h,fill,stroke,1.4,12,dash)
        if label: s.text(x+12,y+20,label,ls,600,lc)
    def diamond(s,cx,cy,w,h,fam,t,ts=15):
        f,k=FAM[fam]; s.add(f'<polygon points="{cx},{cy-h/2} {cx+w/2},{cy} {cx},{cy+h/2} {cx-w/2},{cy}" fill="{f}" stroke="{k}" stroke-width="1.8"/>')
        lines=t.split('\n'); y0=cy-(len(lines)-1)*ts*0.62+ts*0.35
        for i,l in enumerate(lines): s.text(cx,y0+i*ts*1.25,l,ts,600,INK,'middle')
    def brace(s,x1,x2,y,label,down=True,c='#3A4456',size=14):
        m=(x1+x2)/2; q=8 if down else -8
        s.add(f'<path d="M{x1} {y} Q{x1} {y+q} {x1+10} {y+q} L{m-8} {y+q} Q{m} {y+q} {m} {y+2*q} Q{m} {y+q} {m+8} {y+q} L{x2-10} {y+q} Q{x2} {y+q} {x2} {y}" fill="none" stroke="{c}" stroke-width="1.4"/>')
        s.text(m,y+2*q+(16 if down else -6),label,size,500,c,'middle',mono=True)
    def legend(s,x,y,items,cols=None,size=14,colw=210):
        cols=cols or len(items)
        for i,(fam,lab) in enumerate(items):
            xx=x+(i%cols)*colw; yy=y+(i//cols)*26
            if fam in FAM: f,k=FAM[fam]; s.rect(xx,yy-13,24,16,f,k,1.5,3)
            elif fam=='dash': s.add(f'<path d="M{xx} {yy-5} L{xx+24} {yy-5}" stroke="#2B2F36" stroke-width="1.8" stroke-dasharray="6 4"/>')
            elif fam=='arrow': s.arrow([(xx,yy-5),(xx+24,yy-5)])
            elif fam=='mask': s.tokens(xx+4,yy-13,1,'#fff',cell=15,masked=(0,))
            s.text(xx+32,yy,lab,size,500,'#2A3242')
    def caption(s,num,text,size=17.5):
        lines=text.split('\n'); y=s.H-24-size*1.35*len(lines)+size*0.2-14
        s.add(f'<line x1="40" y1="{y-size*1.2}" x2="{s.W-40}" y2="{y-size*1.2}" stroke="#D5D9E0" stroke-width="1"/>')
        for i,l in enumerate(lines):
            pre=f'<tspan font-weight="700">Figure {num}.</tspan> ' if i==0 else ''
            s.add(f'<text x="40" y="{y+i*size*1.35}" font-family="IBM Plex Sans" font-size="{size}" fill="{INK}">{pre}{mk(l,size)}</text>')
    def badge(s,t='Rendered illustration'):
        w=len(t)*8.3+26; x=s.W-w-22; y=s.H-34
        s.add(f'<rect x="{x}" y="{y}" width="{w}" height="24" rx="5" fill="#0B1A2B" stroke="#F5A623" stroke-width="1.6"/>')
        s.text(x+w/2,y+16.5,t,13.5,600,'#ECF2F8','middle')
    def svg(s):
        mk=''.join(f'<marker id="ah{c.strip("#")}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{c}"/></marker>' for c in getattr(s,'markers',set()))
        flt='<filter id="grey"><feColorMatrix type="saturate" values="0.05"/></filter>'
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="{s.W}" height="{s.H}" viewBox="0 0 {s.W} {s.H}"><defs>{mk}{flt}</defs><rect width="100%" height="100%" fill="{s.bg}"/>'+''.join(s.e)+'</svg>'
    def render(s,out_png,scale=2):
        out_png=os.path.abspath(out_png); hp=out_png.replace('.png','.html')
        open(hp,'w').write(f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;padding:0;background:#fff}}</style></head><body>{s.svg()}</body></html>')
        subprocess.run(['google-chrome','--headless=new','--no-sandbox','--disable-gpu','--hide-scrollbars',f'--force-device-scale-factor={scale}',f'--window-size={s.W},{s.H}',f'--screenshot={out_png}','file://'+hp],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=120)
        im=Image.open(out_png); 
        if im.size!=(s.W*scale,s.H*scale): im=im.crop((0,0,s.W*scale,s.H*scale)); im.save(out_png)
        return out_png
def preview(png,w=1600):
    im=Image.open(png).convert('RGB'); im.thumbnail((w,w*2)); p=png.replace('.png','_view.jpg'); im.save(p,quality=88); return p
