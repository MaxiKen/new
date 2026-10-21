import cv2, numpy as np

def masked_ncc(img, tpl, mask):
    """img HxWx3 f32, tpl hxwx3 f32, mask hxw 0/1 f32 -> masked NCC map, channels pooled correctly."""
    M=mask.astype(np.float32)
    n=float(M.sum())
    muT=(tpl*M[:,:,None]).sum(axis=(0,1))/n
    Tc=((tpl-muT)*M[:,:,None]).astype(np.float32)
    denT=float((Tc*Tc).sum())
    Hp,Wp=img.shape[0]-tpl.shape[0]+1,img.shape[1]-tpl.shape[1]+1
    if denT<=1e-6 or Hp<=0 or Wp<=0: return np.zeros((max(Hp,0),max(Wp,0)),np.float32)
    num=np.zeros((Hp,Wp),np.float64); denI=np.zeros((Hp,Wp),np.float64)
    for c in range(3):
        Ic=img[:,:,c]
        num+=cv2.matchTemplate(Ic,Tc[:,:,c],cv2.TM_CCORR).astype(np.float64)
        S_I=cv2.matchTemplate(Ic,M,cv2.TM_CCORR).astype(np.float64)
        S_I2=cv2.matchTemplate(Ic*Ic,M,cv2.TM_CCORR).astype(np.float64)
        denI+=S_I2-(S_I*S_I)/n
    denI=np.maximum(denI,0)
    denom=np.sqrt(denI*denT)
    out=np.divide(num,denom,out=np.zeros_like(num),where=denom>1e-3)
    return out.astype(np.float32)

def scale_tpl(tpl,mask,s):
    if abs(s-1.0)<1e-9: return tpl,mask
    t2=cv2.resize(tpl,None,fx=s,fy=s,interpolation=cv2.INTER_AREA if s<1 else cv2.INTER_LINEAR)
    m2=cv2.resize(mask,None,fx=s,fy=s,interpolation=cv2.INTER_AREA)
    m2=(m2>0.35).astype(np.float32)
    if m2.shape!=t2.shape[:2]:
        m2=cv2.resize(m2,(t2.shape[1],t2.shape[0]),interpolation=cv2.INTER_NEAREST)
    return t2,m2
