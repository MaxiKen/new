import pandas as pd, pickle, re, glob
import geopandas as gpd
names=set()
for pat in ['shapefiles/**/*place*.shp','shapefiles/**/*town*.shp','shapefiles/**/*capital*.shp']:
    for f in glob.glob(pat,recursive=True):
        try:
            g=gpd.read_file(f)
            col=[c for c in g.columns if 'name' in c.lower()]
            if col:
                for v in g[col[0]].dropna().astype(str): names.add(re.sub(r'[^A-Z]','',v.upper()))
            print(f, len(g), col[:1])
        except Exception as e: print(f,e)
print("gazetteer names:",len(names))
def norm(s): return re.sub(r'[^A-Z]','',str(s).upper())
tab=pd.read_pickle('work/min/tables_final.pkl')
SING={'C','E','F','M','P','R','U','W'}
repairs=0
for idx,r in tab.iterrows():
    codes=list(r.codes_list)
    if not codes: continue
    # candidate: move k leading tokens (single letters, or Ba/Ta when following a single) to locality
    best=None
    orig_in=norm(r.locality) in names
    letters=''
    for k in range(1,min(3,len(codes))+1):
        tok=codes[k-1]
        if len(tok)==1 and tok in SING: letters+=tok
        elif k>1 and tok in ('Ba','Ta','Ma'): letters+=tok
        else: break
        cand_loc=(str(r.locality).rstrip()+letters.lower()) if not str(r.locality).isupper() else (str(r.locality).rstrip()+letters)
        # append to last token: our locality already is last-token-truncated form; simply concatenate ignoring spaces for gazetteer check
        if norm(cand_loc) in names and not orig_in:
            best=(k,cand_loc)
    if best:
        k,cand_loc=best
        # rebuild locality display: append letters to last word
        loc=str(r.locality)
        add=letters if loc.isupper() else letters.lower()
        newloc=loc.rstrip()+add
        tab.at[idx,'locality']=newloc
        tab.at[idx,'codes_list']=codes[k:]
        repairs+=1
        print(f"REPAIR {r.zone}{int(r.link_num)}{r.link_suffix}: {r.locality!r}+{letters} -> {newloc!r}, codes {codes} -> {codes[k:]}")
print("total repairs:",repairs)
tab.to_pickle('work/min/tables_final.pkl'); tab.to_csv('work/min/tables_final.csv',index=False)
