import pandas as pd, numpy as np, re, pickle, itertools
from collections import Counter
from functools import lru_cache

df=pd.read_csv('work/min/tables_raw2.csv')
SEGMENTS=[(0,340,1295,'A',1),(0,1295,2100,'B',1),
 (1,340,1025,'B',86),(1,1025,1900,'C',1),
 (2,340,1950,'D',1),(3,340,1800,'E',1),
 (4,340,1235,'E',151),(4,1235,2050,'F',1),
 (5,340,1700,'F',83),(6,340,1800,'G',1),(7,340,1150,'G',159)]
CMM={'I':['1'],'l':['1'],'O':['0'],'S':['5','6'],'B':['8'],'Z':['2','7'],'E':['6','8'],'G':['6','9']}
CONF={'6':'8','8':'6','0':'9','9':'0','1':'7','7':'1','3':'8','5':'6'}
DIGMAP=set('0123456789')|set(CMM)

VOCAB=set('Au Ag Ab Aq Ba Bc Bcl Be Bi Bit Bn Br Bx C Ca Cl Cor Cr Cu Cy Dl Dt Ds E Fe Fp Fc Fr F Gm Gn Gr Grl Gvl Gs Gt Gy Ka Ks Ky Lg Li Lp Ls M Mb Mc Mg Ml Mn Mo Ms Mu Mz Na Nb Ni Oil P Pb PbS Ps Py Qa Qs Qz Rb Ru Sd Sl Sn SS St Ta Tc Tm To Tpz Tr Ts U Us W Wa Zn Zr Il Ilm R'.split())
NORM={'CI':'Cl','Ci':'Cl','Pbs':'PbS','ilm':'Ilm','ILM':'Ilm','MI':'Ml','Mi':'Ml'}
def norm_code(c):
    if c in NORM: return NORM[c]
    for v in VOCAB:
        if v.lower()==c.lower(): return v
    return c
def tokenize_compact(s):
    if not s: return []
    @lru_cache(maxsize=None)
    def go(i):
        if i==len(s): return ()
        for L in (3,2,1):
            if i+L<=len(s):
                pc=norm_code(s[i:i+L])
                if pc in VOCAB:
                    rest=go(i+L)
                    if rest is not None: return (pc,)+rest
        return None
    r=go(0)
    return list(r) if r is not None else None

def number_options(left):
    """Return list of (value, rest, tier): tier0=direct map, tier1=variants."""
    s=left.lstrip(' .')
    # capture spaced leading digit-mappable chars: e.g. 'S I.Fagam', '10S ok oto', '199Godogodo'
    m=re.match(r'^([0-9IlOSBZEG](?:\s*[0-9IlOSBZEG]){0,3})(.*)$', s, re.S)
    if not m: return []
    rawprefix_g, tail = m.group(1), m.group(2)
    opts=[]
    # consider rawprefix lengths: full spaced group, and sub-prefixes when glued to locality in same token
    cands_prefix=[]
    grp=rawprefix_g
    cands_prefix.append(grp)
    # also prefixes split inside the group (by chars, respecting spaces removed variants)
    chars=[c for c in grp if not c.isspace()]
    for k in range(1,len(chars)):
        cands_prefix.append(''.join(chars[:k]))
    for pref in cands_prefix:
        pref_ns=''.join(c for c in pref if not c.isspace())
        # rest = remainder of original string after pref_ns chars consumed from s (skip spaces)
        idx=0; consumed=0
        while idx<len(s) and consumed<len(pref_ns):
            if not s[idx].isspace(): consumed+=1
            idx+=1
        rest=s[idx:]
        # tier0: first mapping choice per char; tier1: all combos + confusion subs
        pools=[CMM.get(c,[c]) for c in pref_ns]
        combos=set(''.join(p) for p in itertools.product(*pools)) if pref_ns else set()
        direct=''.join(p[0] for p in pools)
        vals={}
        if direct.isdigit(): vals[int(direct)]=0
        for cb in combos:
            if cb.isdigit(): vals.setdefault(int(cb),1)
            for i,ch in enumerate(cb):
                if ch in CONF:
                    v=int(cb[:i]+CONF[ch]+cb[i+1:])
                    vals.setdefault(v,1)
        for v,tier in vals.items():
            if 1<=v<=260: opts.append((v,rest,tier,len(pref_ns)))
        # reinterpretation: last char is letter of locality (199Godogodo / 830ra)
        if len(pref_ns)>=2 and pref_ns[-1] in CMM:
            letter='O' if pref_ns[-1]=='O' else pref_ns[-1]
            rest2=letter+rest
            pools2=[CMM.get(c,[c]) for c in pref_ns[:-1]]
            combos2=set(''.join(p) for p in itertools.product(*pools2))
            for cb in combos2:
                if cb.isdigit():
                    v=int(cb)
                    if 1<=v<=260: opts.append((v,rest2,1,len(pref_ns)-1))
    return opts

def choose_number(opts, expected):
    def suffix_split(rest):
        r=rest.lstrip('. ')
        m=re.match(r'^([A-Z])(?=[A-Z][a-z])', r)
        if m: return m.group(1), r[1:]
        return '', r
    if not opts: return None,'','',True
    tier0={o[0] for o in opts if o[2]==0}
    allv={o[0] for o in opts}
    chosen=None
    if expected in tier0: chosen=expected
    elif expected in allv: chosen=expected
    elif [c for c in tier0 if expected<c<=expected+3]: chosen=min(c for c in tier0 if c>expected)
    elif [c for c in tier0 if expected-6<=c<expected]: chosen=max(c for c in tier0 if c<expected)
    elif [c for c in allv if expected<c<=expected+3]: chosen=min(c for c in allv if c>expected)
    elif [c for c in allv if expected-6<=c<expected]: chosen=max(c for c in allv if c<expected)
    if chosen is None:
        o=sorted(opts,key=lambda o:(o[2],abs(o[0]-expected)))[0]
        sfx,rest=suffix_split(o[1]); return expected,rest,sfx,True
    pool=[o for o in opts if o[0]==chosen]
    pool.sort(key=lambda o:(o[2], 0 if re.match(r'^[.\s]*([A-Z(]|$)',o[1]) else 1, -o[3]))
    sfx,rest=suffix_split(pool[0][1])
    return chosen,rest,sfx,False

def boundaries_of(rest):
    """letter-index positions where a code-suffix may start"""
    out=[]; prev=''; li=-1
    for ch in rest:
        if ch.isalpha():
            li+=1
            if prev in ' .,/(' or (ch.isupper() and prev.islower()):
                out.append(li)
            prev=ch
        elif ch in ' .,/(':
            prev=ch
    return out

def split_rest_at_letter(rest, letter_idx):
    cnt=-1
    for j,ch in enumerate(rest):
        if ch.isalpha():
            cnt+=1
            if cnt==letter_idx: return rest[:j], rest[j:]
    return rest,''

def parse_row_codes(rest, codes_raw):
    """Returns (locality_rest, codes_list). Tries embedded suffix + column combined tokenization."""
    col_compact=''
    if codes_raw is not None and str(codes_raw)!='nan':
        col_compact=re.sub(r'[^A-Za-z]','',str(codes_raw))
    letters=''.join(c for c in rest if c.isalpha())
    n=len(letters)
    bnds=[b for b in boundaries_of(rest) if b>=2 and (n-b)<=12]
    # try earliest boundary first (longest suffix)
    for b in bnds:
        suf=letters[b:]
        tt=tokenize_compact(suf+col_compact)
        if tt:
            loc,_=split_rest_at_letter(rest,b)
            return loc,tt
    # column alone
    if col_compact:
        tt=tokenize_compact(col_compact)
        if tt is not None: return rest,tt
    # embedded alone (latest boundaries give shorter suffixes; try all)
    for b in bnds:
        tt=tokenize_compact(letters[b:])
        if tt:
            loc,_=split_rest_at_letter(rest,b)
            return loc,tt+(['?'+col_compact] if col_compact else [])
    # separator-aware column parse with bleed suffix
    if col_compact:
        for i in range(2,len(col_compact)):
            if col_compact[i].isupper():
                tt=tokenize_compact(col_compact[i:])
                if tt: return rest+' '+col_compact[:i], tt
        return rest,['?'+col_compact]
    return rest,[]

def clean_locality(s):
    s=re.sub(r'\s+',' ',s).strip(' .,')
    if not s: return s
    # split tokens at lowercase->uppercase transitions (glued words), keep hyphen parts together
    toks=[]
    for t in s.split(' '):
        parts=re.split(r'(?<=[a-z])(?=[A-Z])', t)
        toks+=parts
    out=[]
    for t in toks:
        if not t: continue
        if out and (t[0].islower() or (len(out[-1])==1 and out[-1].isupper()) or (len(t)==1 and t.isupper() and out[-1].isupper())):
            # hyphen handling: if prev ends with '-' just append
            out[-1]=out[-1]+t
        else:
            out.append(t)
    s=' '.join(out)
    for _ in range(3):
        s2=re.sub(r'\b([A-Z]) ([a-z]{2,})', r'\1\2', s)
        if s2==s: break
        s=s2
    return s.strip(' .,')

rows_out=[]; anomalies=[]
for blk,ymin,ymax,zone,first in SEGMENTS:
    sub=df[(df.blk==blk)&(df.y>=ymin)&(df.y<ymax)].sort_values('y')
    expected=first; cont=[]; seen=Counter()
    for _,r in sub.iterrows():
        opts=number_options(str(r.left))
        if not opts:
            cont.append((str(r.left),str(r.codes_raw))); continue
        link,rest,sfx,anom=choose_number(opts,expected)
        if anom: anomalies.append((zone,expected,r.left))
        if link>=expected: expected=link+1
        seen[link]+=1
        autosfx='' if seen[link]==1 else chr(ord('A')+seen[link]-2)
        loc_rest,codes=parse_row_codes(rest, r.codes_raw)
        loc=clean_locality(loc_rest)
        if cont:
            for cl,cc in cont:
                clc=re.sub(r'[^A-Za-z]','',cl)
                t2=tokenize_compact(clc) if clc else None
                if t2: codes+=t2
                else:
                    _,c2=parse_row_codes('',cc)
                    if c2 and not any(x.startswith('?') for x in c2): codes+=c2
                    else: loc=(loc+' '+clean_locality(cl)).strip()
            cont=[]
        rows_out.append({'zone':zone,'link_num':link,'link_suffix':(sfx or autosfx),'locality':loc,
                         'codes_list':codes,'codes_raw':str(r.codes_raw),'blk':int(blk),'y':float(r.y),
                         'left_raw':r.left,'num_anomaly':anom})
tab=pd.DataFrame(rows_out)
print(f"rows={len(tab)} anomalies={len(anomalies)} {anomalies[:10]}")
for z in 'ABCDEFG':
    s=tab[tab.zone==z]; ln=s.link_num.astype(int)
    dups=sorted([k for k,v in Counter(ln).items() if v>1])
    print(f" {z}: n={len(s)} link {ln.min()}..{ln.max()} dups={dups} missing={sorted(set(range(ln.min(),ln.max()+1))-set(ln))[:14]}")
cnt=Counter()
for cl in tab.codes_list: cnt.update(cl)
unk={k:v for k,v in cnt.items() if k.startswith('?')}
print(f"\ncode freq total={sum(cnt.values())} unknown={sum(unk.values())} {dict(Counter(unk).most_common(15))}")
print("top:",dict(Counter({k:v for k,v in cnt.items() if not k.startswith('?')}).most_common(25)))
emp=tab[tab.codes_list.apply(len)==0]
print(f"\nempty-code rows: {len(emp)}")
print(emp[['zone','link_num','link_suffix','locality','left_raw','codes_raw']].to_string(index=False))
qr=tab[tab.codes_list.apply(lambda c:any(x.startswith('?') for x in c))]
print(f"\nunknown-token rows: {len(qr)}")
print(qr[['zone','link_num','locality','codes_list','codes_raw']].head(25).to_string(index=False))
tab.to_csv('work/min/tables_final.csv',index=False)
pickle.dump(tab,open('work/min/tables_final.pkl','wb'))
