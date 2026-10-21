import pandas as pd, pickle, re, unicodedata
import geopandas as gpd
def norm(s):
    s=unicodedata.normalize('NFKD',str(s)); s=''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^A-Z]','',s.upper())
names=set()
g=gpd.read_file('shapefiles/nigeria_online_layers/populated_places/populated_places.shp')
for v in g.PLACE.dropna(): names.add(norm(v))
for v in g.ALIASES.dropna():
    for part in str(v).split(';'): names.add(norm(part))
t=gpd.read_file('shapefiles/nigeria_online_layers/towns/towns.shp')
for v in t.ADM2_NAME.dropna(): names.add(norm(v))
tab=pd.read_pickle('work/min/tables_final.pkl')
# manual fixes first
def fix(zone,num,suf,loc,codes):
    m=(tab.zone==zone)&(tab.link_num==num)&(tab.link_suffix==suf)
    for ix in tab.index[m]:
        tab.at[ix,'locality']=loc; tab.at[ix,'codes_list']=codes; print("MAN",zone,num,loc,codes)
fix('D',33,'','Bakura',['Be','Gm'])
fix('G',23,'','Arufu',['Fr'])
fix('G',25,'','Arufu',['Pb'])
SING={'C','E','F','M','P','R','U','W'}
rep=0
for idx,r in tab.iterrows():
    codes=list(r.codes_list); loc=str(r.locality)
    if not codes: continue
    # A) longest gazetteer move of leading tokens (singles + one 2-letter) if it lengthens locality into gazetteer
    best=None; letters=''
    for k in range(min(4,len(codes))):
        tok=codes[k]
        if len(tok)==1 and tok in SING: letters+=tok
        elif k>=1 and tok in ('Ba','Ta','Ma','Fu'): letters+=tok
        else: break
        cand=loc.rstrip()+(letters if loc.isupper() else letters.lower())
        if norm(cand) in names and norm(cand)!=norm(loc):
            best=(k+1,cand,letters)
    if best:
        k,cand,letters=best
        # only apply if current locality not in gazetteer OR cand longer & codes had >=2 singles
        if norm(loc) not in names or sum(1 for c in codes[:k] if len(c)==1)>=2:
            tab.at[idx,'locality']=cand; tab.at[idx,'codes_list']=codes[k:]; rep+=1
            print(f"GAZ3 {r.zone}{int(r.link_num)}{r.link_suffix}: {loc!r}->{cand!r} {codes}->{codes[k:]}")
            continue
    # B) lowercase boundary fragment (any row): move tokens covered by that fragment
    left=str(r.left_raw)
    frags=[f for f in re.split(r'\s+',left.strip()) if f]
    Lo=re.sub(r'[^A-Za-z]','',loc)
    acc=''; start=None
    for fi,f in enumerate(frags):
        fl=re.sub(r'[^A-Za-z]','',f)
        if not fl: continue
        if len(acc)<len(Lo) and Lo.startswith(acc+fl):
            acc+=fl
            if acc==Lo: start=fi+1; break
        elif len(acc)<len(Lo) and (acc+fl).startswith(Lo):
            start=None; break
        else:
            start=None; break
    if start is not None and start<len(frags):
        f0=frags[start]
        if f0 and f0[0].islower():
            frag_letters=re.sub(r'[^A-Za-z]','',f0)
            acc2=''; k=0
            for tok in codes:
                if frag_letters.lower().startswith((acc2+tok).lower()): acc2+=tok; k+=1
                else: break
            if k>=1:
                add=frag_letters if loc.isupper() else frag_letters.lower()
                tab.at[idx,'locality']=loc.rstrip()+add
                tab.at[idx,'codes_list']=codes[k:]; rep+=1
                print(f"LOW3 {r.zone}{int(r.link_num)}{r.link_suffix}: {loc!r}->{loc.rstrip()+add!r} {codes}->{codes[k:]} (frag {f0!r})")
print("repairs v3:",rep)
tab.to_pickle('work/min/tables_final.pkl'); tab.to_csv('work/min/tables_final.csv',index=False)
