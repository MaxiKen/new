import numpy as np, sys
from PIL import Image

def classes_from(f, ncol=64, minarea=0.0008):
    im=Image.open(f).convert('RGB')
    im.thumbnail((1400,1400), Image.LANCZOS)
    q=im.quantize(colors=ncol, method=Image.MEDIANCUT, dither=Image.NONE)
    pal=np.array(q.getpalette(),dtype=np.int64).reshape(-1,3)[:ncol]
    a=np.asarray(q)
    cnt=np.bincount(a.ravel(),minlength=ncol)
    idx=[i for i in np.argsort(-cnt) if cnt[i]/a.size>minarea]
    # merge similar
    keep=[]
    for i in idx:
        c=pal[i]
        if not any(np.abs(c-pal[j]).sum()<34 for j in keep):
            keep.append(i)
    return pal[keep], np.array([cnt[i] for i in keep]), a.size

def render(f, cols=150, ncol=64, x0=0.0,x1=1.0,y0=0.0,y1=1.0):
    im=Image.open(f).convert('RGB')
    W,H=im.size
    im=im.crop((int(x0*W),int(y0*H),int(x1*W),int(y1*H)))
    rows=max(1,int(round(cols*im.size[1]/im.size[0]/2.05)))
    im=im.resize((cols,rows), Image.LANCZOS)
    a=np.asarray(im,dtype=np.int64)
    pal,cnt,tot=classes_from(f,ncol)
    # classify each pixel
    d=((a[:,:,None,:]-pal[None,None,:,:])**2).sum(axis=3)
    lab=d.argmin(axis=2)
    chars="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*+=~<>?!"
    out=[]
    for r in range(rows):
        out.append(''.join(chars[lab[r,c]%len(chars)] if len(chars)>0 else '?' for c in range(cols)))
    print(f'--- {f}  region x[{x0},{x1}] y[{y0},{y1}]  grid {cols}x{rows}')
    print('\n'.join(out))
    print('LEGEND:')
    for k,i in enumerate(range(len(pal))):
        print(f'   {chars[k%len(chars)]}  rgb{tuple(pal[i])}  {100*cnt[i]/tot:5.2f}%')
    return pal,cnt

if __name__=='__main__':
    f=sys.argv[1]; cols=int(sys.argv[2]) if len(sys.argv)>2 else 150
    render(f,cols)
