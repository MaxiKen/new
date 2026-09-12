import re,os,glob,collections,unicodedata,json
ROOT='/home/user/new'
# chapter lengths from reference
LEN={}
for n in range(1,115):
    LEN[n]=max(int(m.group(1)) for m in re.finditer(r'^(\d+) \|',open(ROOT+'/translation/%03d.txt'%n,encoding='utf-8').read(),re.M))
# name map from headings
NAME={}
for p in sorted(glob.glob(ROOT+'/expanded/*.md')):
    n=int(os.path.basename(p)[:3])
    for m in re.finditer(r'^## Sūrah (.+?) (\d+):(\d+)',open(p,encoding='utf-8').read(),re.M):
        NAME.setdefault(int(m.group(2)),set()).add(m.group(1).strip())
# 1) out of range verse citations
CITE=re.compile(r'\((?:\s*(?:Qur[\'\u2019]?an|Q\.?)\s*)?(\d{1,3})\s*:\s*(\d{1,3})(?:\s*[-–]\s*(\d{1,3}))?\s*\)')
oob=[]
for p in sorted(glob.glob(ROOT+'/expanded/*.md')):
    n=int(os.path.basename(p)[:3])
    for i,line in enumerate(open(p,encoding='utf-8')):
        for m in CITE.finditer(line):
            ch,v,e=int(m.group(1)),int(m.group(2)),int(m.group(3) or m.group(2))
            if ch>114 or ch<1: oob.append((n,i+1,ch,v,'chapter out of range',line.strip()[:120])); continue
            if v>LEN[ch] or e>LEN[ch]: oob.append((n,i+1,ch,v,'verse beyond end of sūrah (%d has %d verses)'%(ch,LEN[ch]),line.strip()[:150]))
print('1) OUT-OF-RANGE Qur\'an citations:',len(oob))
for r in oob[:25]: print('   %03d.md:%d  %d:%d  %s | %s'%r)
# 2) surah name vs number
pat=re.compile(r'(?:Sūrat|Sūrah|Surat|Surah)\s+([A-Za-z\u2019\u02be\u02bf\u02b9\u02ba\u2018\u2019\-ʿʾāīūṣḍṭẓḥ]+)[\s,]*\(?(\d{1,3}):(\d{1,3})')
known={'al-Fātiḥah':1}
# build canonical name->chapter from headings (majority)
allnames=collections.defaultdict(collections.Counter)
for p in sorted(glob.glob(ROOT+'/expanded/*.md')):
    n=int(os.path.basename(p)[:3])
    for m in re.finditer(r'^## Sūrah (.+?) (\d+):',open(p,encoding='utf-8').read(),re.M):
        allnames[m.group(1).strip()][int(m.group(2))]+=1
name2ch={k:v.most_common(1)[0][0] for k,v in allnames.items()}
badname=[]
for p in sorted(glob.glob(ROOT+'/expanded/*.md')):
    n=int(os.path.basename(p)[:3])
    for i,line in enumerate(open(p,encoding='utf-8')):
        for m in pat.finditer(line):
            nm,ch=m.group(1).strip(),int(m.group(2))
            if nm in name2ch and name2ch[nm]!=ch and ch<=114:
                badname.append((n,i+1,nm,ch,name2ch[nm],line.strip()[:150]))
print('\n2) SŪRAH NAME / CHAPTER MISMATCHES:',len(badname))
seen=set()
for r in badname:
    k=(r[2],r[3])
    if k in seen: continue
    seen.add(k)
    print('   %03d.md:%d  "%s" cited with chapter %d, but %s is chapter %d | %s'%r)
# 3) hadith number plausibility
MAX={'Bukhārī':7563,'Muslim':3033,'Abū Dāwūd':5274,'Tirmidhī':3956,'Nasāʾī':5761,'Ibn Mājah':4341,'Mālik':1857,'Aḥmad':27647,'Dārimī':3367,'Ḥākim':9000,'Bayhaqī':21000,'Ṭabarānī':25000}
pat_h=re.compile(r'\b(al-[A-Za-zāīūʿʾ\u02be\u02bf]+|Abū Dāwūd|Ibn Mājah|Aḥmad|al-Bukhārī|al-Tirmidhī|al-Nasāʾī|Muslim)\s*[(\s]\s*(?:no\.\s*)?(\d{2,6})')
viol=[]
for p in sorted(glob.glob(ROOT+'/expanded/*.md')):
    n=int(os.path.basename(p)[:3])
    txt=open(p,encoding='utf-8').read()
    for i,line in enumerate(txt.split('\n')):
        for m in re.finditer(r'(al-Bukh[āa]r[īi]|al-Tirmidh[īi]|al-Nas[āa][ʾ\']?[īi]|Abū Dāwūd|Ibn Mājah|Muslim|Aḥmad|Mālik|al-Dārimī|al-Ḥākim|al-Bayhaqī|al-Ṭabarānī)\s*[,\s]*\(?(?:no\.\s*)?(\d{1,4})\)?',line):
            coll,num=m.group(1),int(m.group(2))
            key={'al-Bukhārī':'Bukhārī','al-Bukhari':'Bukhārī','al-Tirmidhī':'Tirmidhī','al-Tirmidhi':'Tirmidhī','al-Nasāʾī':'Nasāʾī','al-Nasaʾi':'Nasāʾī','Muslim':'Muslim','Abū Dāwūd':'Abū Dāwūd','Ibn Mājah':'Ibn Mājah','Aḥmad':'Aḥmad','Mālik':'Mālik','al-Dārimī':'Dārimī','al-Ḥākim':'Ḥākim','al-Bayhaqī':'Bayhaqī','al-Ṭabarānī':'Ṭabarānī'}.get(coll)
            if key and num>MAX.get(key,10**9): viol.append((n,i+1,coll,num,MAX[key],line.strip()[:130]))
print('\n3) HADITH NUMBERS EXCEEDING COLLECTION SIZE:',len(viol))
for r in viol[:20]: print('   %03d.md:%d  %s %d (max ~%d) | %s'%r)
# 4) most-cited hadith numbers per collection (consistency)
cnt=collections.Counter()
for p in sorted(glob.glob(ROOT+'/expanded/*.md')):
    for m in re.finditer(r'(al-Bukh[āa]r[īi]|al-Tirmidh[īi]|al-Nas[āa][ʾ\']?[īi]|Abū Dāwūd|Ibn Mājah|Muslim|Aḥmad)\s*[,\s]*\(?(?:no\.\s*)?(\d{1,4})\)?',open(p,encoding='utf-8').read()):
        cnt[(m.group(1),int(m.group(2)))]+=1
print('\n4) top 20 most-cited hadith numbers:')
for k,v in cnt.most_common(20): print('   %-14s %-6d cited %d times'%(k[0],k[1],v))
