import pandas as pd, pickle, re, unicodedata
import geopandas as gpd
def norm(s):
    s=unicodedata.normalize('NFKD',str(s))
    s=''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^A-Z]','',s.upper())
names=set()
g=gpd.read_file('shapefiles/nigeria_online_layers/populated_places/populated_places.shp')
for v in g.PLACE.dropna(): names.add(norm(v))
for v in g.ALIASES.dropna():
    for part in str(v).split(';'): names.add(norm(part))
t=gpd.read_file('shapefiles/nigeria_online_layers/towns/towns.shp')
for v in t.ADM2_NAME.dropna(): names.add(norm(v))
print("gazetteer:",len(names))
tab=pd.read_pickle('work/min/tables_final.pkl')
# fix display bug from v1
tab.loc[tab.locality=='AWEBa','locality']='AWE'
SING={'C','E','F','M','P','R','U','W'}
rep=0
for idx,r in tab.iterrows():
    codes=list(r.codes_list)
    if not codes or codes[0] not in SING: continue
    loc=str(r.locality)
    if norm(loc) in names: continue
    # try moving leading tokens: singles, then optionally one 2-letter (Ba/Ta/Ma)
    letters=''; moved=0; found=False
    for k in range(min(3,len(codes))):
        tok=codes[k]
        if len(tok)==1 and tok in SING: letters+=tok
        elif k>=1 and tok in ('Ba','Ta','Ma'): letters+=tok
        else: break
        cand=loc.rstrip()+(letters if loc.isupper() else letters.lower())
        if norm(cand) in names:
            # rebuild proper display: only the moved letters append
            add=letters if loc.isupper() else letters.lower()
            tab.at[idx,'locality']=loc.rstrip()+add
            tab.at[idx,'codes_list']=codes[k+1:]
            print(f"GAZ {r.zone}{int(r.link_num)}{r.link_suffix}: {loc!r} -> {loc.rstrip()+add!r} codes {codes}->{codes[k+1:]}")
            rep+=1; found=True; break
    if found: continue
    # lowercase-fragment rule (embedded-derived rows only)
    if str(r.codes_raw) not in ('nan',''): continue
    left=str(r.left_raw)
    frags=[f for f in re.split(r'\s+',left.strip()) if f]
    # letters of our locality
    Lo=re.sub(r'[^A-Za-z]','',loc)
    acc=''; start_frag=None
    for fi,f in enumerate(frags):
        fl=re.sub(r'[^A-Za-z]','',f)
        if acc+fl==Lo[:len(acc+fl)] and len(acc+fl)<=len(Lo):
            acc+=fl
            if acc==Lo: start_frag=fi+1; break
        else:
            # fragment straddles boundary (glued number+name etc.) - give up precise
            start_frag=None; break
    if start_frag is not None and start_frag<len(frags):
        f0=frags[start_frag]
        if f0 and f0[0].islower():
            # letters of this fragment belong to locality; move code tokens covering them
            frag_letters=re.sub(r'[^A-Za-z]','',f0)
            # how many leading code tokens' letters are within frag_letters (case-insensitive prefix match)
            acc2=''; k=0
            for tok in codes:
                if frag_letters.lower().startswith((acc2+tok).lower()):
                    acc2+=tok; k+=1
                else: break
            if k>=1 and acc2.lower()==frag_letters.lower()[:len(acc2)]:
                add=frag_letters if loc.isupper() else frag_letters.lower()
                # if fragment longer than tokens moved (e.g. 'uba' vs U+Ba equal) use fragment letters
                tab.at[idx,'locality']=loc.rstrip()+add
                tab.at[idx,'codes_list']=codes[k:]
                print(f"LOW {r.zone}{int(r.link_num)}{r.link_suffix}: {loc!r} -> {loc.rstrip()+add!r} codes {codes}->{codes[k:]} (frag {f0!r})")
                rep+=1
print("repairs v2:",rep)
tab.to_pickle('work/min/tables_final.pkl'); tab.to_csv('work/min/tables_final.csv',index=False)
from collections import Counter
cnt=Counter()
for c in tab.codes_list: cnt.update(c)
print("single-letter code counts now:",{k:cnt[k] for k in ['C','E','F','M','P','R','U','W']})
print("total codes:",sum(cnt.values()))
