#!/usr/bin/env python3
"""Exploratory two-river comparison; raster matching, NOT a survey or CRS proof.
Dependencies: pymupdf numpy scipy shapely matplotlib
"""
import json
from pathlib import Path
import numpy as np
import pymupdf
from scipy.ndimage import distance_transform_edt, map_coordinates
from scipy.optimize import differential_evolution
from shapely.geometry import shape
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
F={'geo':'Geological_Map_of_Nigeria.pdf','min':'Mineral_Resources_Map_of_Nigeria_2023.pdf'}
ref=json.loads((ROOT/'Niger_Benue_Natural_Earth.geojson').read_text())
points={}
for f in ref['features']:
    name=f['properties']['name'];
    if name not in ('Niger','Benue'): continue
    geom=shape(f['geometry']); ls=list(geom.geoms) if hasattr(geom,'geoms') else [geom]; samples=[]
    for line in ls:
        if line.geom_type!='LineString' or line.length<.1: continue
        for d in np.arange(.025,line.length,.025):
            p=line.interpolate(d); samples.append([p.x,p.y])
    points[name]=np.array(samples)

def load(kind):
    p=pymupdf.open(ROOT/F[kind])[0]
    r=pymupdf.Rect(80,90 if kind=='geo' else 359,2050,1693 if kind=='geo' else 1968)
    pix=p.get_pixmap(matrix=pymupdf.Matrix(1,1),clip=r,alpha=False)
    a=np.frombuffer(pix.samples,np.uint8).reshape(pix.height,pix.width,3).astype(np.int16)
    mask=(abs(a[:,:,0]-151)<=8)&(abs(a[:,:,1]-219)<=8)&(abs(a[:,:,2]-242)<=8)
    return r, mask, distance_transform_edt(~mask)

loaded={k:load(k) for k in F}

def page_xy(lon,lat,kind,mode):
    if kind=='geo':return lon*157.593-276.36,2281.63-lat*157.586
    if mode=='grid':return lon*157.5987-288.95,2572.35-lat*157.6015
    return (74.23969+(lon-2.47619)/12.54519*(2051.1915-74.23969),
            (2160-1801.2761)+(14.04668-lat)/10.20997*((2160-192.29888)-(2160-1801.2761)))

def extent(kind,mode):
    r=loaded[kind][0]
    if kind=='geo':return ((r.x0+276.36)/157.593,(r.x1+276.36)/157.593,(2281.63-r.y1)/157.586,(2281.63-r.y0)/157.586)
    if mode=='grid':return ((r.x0+288.95)/157.5987,(r.x1+288.95)/157.5987,(2572.35-r.y1)/157.6015,(2572.35-r.y0)/157.6015)
    def inv(x,y):return (2.47619+(x-74.23969)*12.54519/(2051.1915-74.23969),14.04668-(y-(2160-1801.2761))*10.20997/((2160-192.29888)-(2160-1801.2761)))
    l,t=inv(r.x0,r.y0);rr,b=inv(r.x1,r.y1);return(l,rr,b,t)

def residual(kind,mode,coords,delta=(0,0)):
    r,mask,d=loaded[kind]; lon=coords[:,0]+delta[0];lat=coords[:,1]+delta[1]
    x,y=page_xy(lon,lat,kind,mode)
    return map_coordinates(d,[y-r.y0,x-r.x0],order=1,mode='constant',cval=200)*111.2/157.6

stats={}
for kind,mode in [('geo','grid'),('min','grid'),('min','embedded')]:
    key=kind+'_'+mode;stats[key]={}
    for n,pts in points.items():
        z=residual(kind,mode,pts);stats[key][n]={'samples':len(pts),'median_km':round(float(np.median(z)),2),'p90_km':round(float(np.percentile(z,90)),2),'within_5km_pct':round(float(np.mean(z<5)*100),1)}
    for train,test in [('Niger','Benue'),('Benue','Niger')]:
        opt=differential_evolution(lambda q:np.median(residual(kind,mode,points[train],q)),[(-.25,.25),(-.25,.25)],seed=3,tol=.003,popsize=10)
        stats[key]['fit_'+train]={'reference_to_page_delta_degrees':[round(float(v),6) for v in opt.x], 'training_median_km':round(float(opt.fun),2),'holdout_river':test,'holdout_median_km':round(float(np.median(residual(kind,mode,points[test],opt.x))),2)}
(ROOT/'River_Registration_Results.json').write_text(json.dumps(stats,indent=2)+'\n')
print(json.dumps(stats,indent=2))

fig,axes=plt.subplots(2,2,figsize=(13,9),constrained_layout=True)
configs=[('geo','grid','Geology: printed-grid registration',(0,0)),('min','grid','Minerals: printed-grid registration',(0,0)),('min','embedded','Minerals: embedded registration',(0,0)),('min','embedded','Minerals: experimental river-fit shift',(.0753,.0578))]
for ax,(kind,mode,title,shift) in zip(axes.flat,configs):
    mask=loaded[kind][1]; e=extent(kind,mode); e=(e[0]+shift[0],e[1]+shift[0],e[2]+shift[1],e[3]+shift[1])
    # White = no detected blue water; blue = pixels close to the river fill colour.
    im=np.ones((*mask.shape,3),dtype=np.uint8)*255;im[mask]=[36,97,178]
    ax.imshow(im,extent=e,origin='upper',interpolation='nearest',aspect='auto')
    for f in ref['features']:
        g=shape(f['geometry']);ls=list(g.geoms) if hasattr(g,'geoms') else [g]
        for l in ls:
            if l.geom_type=='LineString':
                xy=np.array(l.coords);ax.plot(xy[:,0],xy[:,1],color='#ee8619',lw=1.15)
    ax.set(xlim=(3.3,12.8),ylim=(7.25,12.5),title=title,xlabel='Longitude (degrees)',ylabel='Latitude (degrees)')
    ax.grid(alpha=.18)
fig.suptitle('Niger and Benue: Natural Earth reference (orange) vs detected PDF water (blue)\nExploratory only: colour mask, generalized rivers, datum not verified',fontsize=13)
fig.savefig(ROOT/'River_Registration_Comparison.png',dpi=150);plt.close(fig)

# A readable map of the fetched reference, including national outline and towns.
fig,ax=plt.subplots(figsize=(9,8),constrained_layout=True)
out=json.loads((ROOT/'Nigeria_Natural_Earth_outline.geojson').read_text())
for f in out['features']:
    g=shape(f['geometry']);parts=list(g.geoms) if hasattr(g,'geoms') else [g]
    for poly in parts:
        xy=np.array(poly.exterior.coords);ax.fill(xy[:,0],xy[:,1],color='#eef1e8',edgecolor='#465849',lw=.8)
for f in ref['features']:
    g=shape(f['geometry']);ls=list(g.geoms) if hasattr(g,'geoms') else [g]
    for l in ls:
        if l.geom_type=='LineString':
            xy=np.array(l.coords);ax.plot(xy[:,0],xy[:,1],color='#1468aa',lw=1.7,label=f['properties']['name'])
ax.scatter([6.767263],[7.785712],s=20,color='#e07616',zorder=5);ax.annotate('Lokoja confluence\n(reference centrelines)',(6.767263,7.785712),xytext=(7.05,7.2),arrowprops={'arrowstyle':'->'},fontsize=8)
ax.set(xlim=(2.5,14.8),ylim=(4,14.3),xlabel='Longitude (°E)',ylabel='Latitude (°N)',title='Nigeria: Natural Earth Niger and Benue river reference\nGeneralized 1:10m centreline, not a surveyed river boundary');ax.grid(alpha=.2)
handles,labels=ax.get_legend_handles_labels();unique=dict(zip(labels,handles));ax.legend(unique.values(),unique.keys(),loc='upper left')
fig.savefig(ROOT/'Nigeria_Rivers_Reference.png',dpi=150);plt.close(fig)
