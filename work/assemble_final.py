import pickle, numpy as np, pandas as pd, geopandas as gpd, json, shutil, os
OUT='deliverables_flat'
# boundary (cleaned)
a=gpd.read_file('shapefiles/nigeria_admin0/nigeria_admin0.shp')
area=a.geometry.to_crs('EPSG:3857').area.iloc[0]/1e6
b=gpd.GeoDataFrame({'fid':[1],'name':[a.NAME.iloc[0]],'formal':[a.FORMAL_EN.iloc[0]],
                    'iso_a3':[a.ISO_A3.iloc[0]],'iso_a2':[a.ISO_A2.iloc[0]],
                    'continent':[a.CONTINENT.iloc[0]],'area_km2':[round(float(area),1)]},
                   geometry=a.geometry.values,crs='EPSG:4326')
b.to_file(f'{OUT}/nigeria_boundary.shp')
print("boundary ok", b.area_km2.iloc[0])
# states
s=gpd.read_file('shapefiles/nigeria_online_layers/state_boundaries/state_boundaries.shp')
s=s.rename(columns={'STATE_NM':'state','ADM1_CODE':'adm1_code','ISO3166_2':'iso_3166_2','TYPE_EN':'type','ALT_NAME':'alt_name'})
s['area_km2']=(s.geometry.to_crs('EPSG:3857').area/1e6).round(1)
s.insert(0,'fid',range(1,len(s)+1))
s=s[['fid','state','type','adm1_code','iso_3166_2','alt_name','area_km2','geometry']]
s.to_file(f'{OUT}/nigeria_states.shp')
print("states ok",len(s))
# minerals final
g=pickle.load(open('work/min/minerals_final_v4.pkl','rb'))
g=g.sort_values(['leg_no','near_num','locality']).reset_index(drop=True)
g['fid']=range(1,len(g)+1)
g=g[['fid','leg_no','mineral','comm_grp','table_code','locality','near_num','id_score','stage','px_x','px_y','lon','lat','link_type','geometry']]
g.to_file(f'{OUT}/nigeria_mineral_occurrences.shp')
print("minerals ok",len(g))
# rivers + labels + pegmatite
r=pickle.load(open('work/min/rivers_final.pkl','rb'))
r.to_file(f'{OUT}/nigeria_rivers.shp')
lab=gpd.read_file('work/min/river_labels_final.shp'); lab.insert(0,'fid',range(1,len(lab)+1))
lab.to_file(f'{OUT}/nigeria_river_labels.shp')
p=gpd.read_file('work/min/pegmatite_labels.shp')
p.to_file(f'{OUT}/nigeria_pegmatite_fields.shp')
print("rivers",len(r),"labels",len(lab),"pegm",len(p))
# enriched legend csv
leg=pd.read_csv('work/min/mineral_legend.csv')
cnt=g.leg_no.value_counts()
leg['occurrences_in_dataset']=leg.legend_no.map(cnt).fillna(0).astype(int)
leg.to_csv(f'{OUT}/mineral_legend.csv',index=False)
print(leg.head(3).to_string())
# localities table transcription
tab=pd.read_pickle('work/min/tables_final.pkl')
CODE2LEG={'Au':26,'Ag':56,'Ab':1,'Aq':6,'Ba':3,'Bc':9,'Bcl':2,'Be':6,'Gm':6,'Bi':7,'Bit':8,'Bn':5,'Br':10,'Bx':4,'C':13,'Cl':12,'Cy':12,'Cor':16,'Ru':16,'Rb':16,'Cr':11,'Cu':15,'Dl':17,'Dt':17,'Ds':18,'E':19,'Fe':33,'Il':33,'Ilm':33,'Fp':20,'Fc':21,'Fr':22,'F':22,'Gn':30,'Gr':27,'Grl':28,'Gvl':28,'Gs':25,'Sd':25,'Gt':23,'Gy':31,'Ka':34,'Wa':34,'Ks':34,'Ky':35,'Lg':38,'Li':66,'Lp':37,'Ls':39,'Us':39,'M':44,'Ms':44,'Mu':44,'Mb':41,'Mc':42,'Mg':45,'Ml':43,'Mn':40,'Mo':46,'Mz':47,'Na':53,'Nb':14,'Sn':14,'Ni':48,'Oil':24,'P':32,'Pb':36,'Zn':36,'PbS':29,'Py':51,'Qa':52,'Qz':52,'Qs':52,'R':52,'Sl':55,'St':55,'SS':54,'Ta':58,'Tc':57,'Tm':61,'To':60,'Tpz':60,'Tr':62,'Ts':59,'U':63,'W':64,'Zr':65,'Ca':67}
name_by_leg=dict(zip(leg.legend_no,leg.point_attribute_name))
def decode(codes):
    out=[]
    for c in codes:
        L=CODE2LEG.get(c)
        out.append(name_by_leg.get(L,c) if L else c)
    seen=[]
    for x in out:
        if x not in seen: seen.append(x)
    return '; '.join(seen)
t=pd.DataFrame({'map_zone':tab.zone,'map_no':tab.link_num.astype(str),'ref':tab.zone+tab.link_num.astype(str),
                'locality':tab.locality,'commodity_codes':tab.codes_list.map(lambda c:'.'.join(c)),
                'minerals_decoded':tab.codes_list.map(decode)})
t=t.sort_values(['map_zone','map_no'],key=lambda s: s.astype(str) if s.name=='map_no' else s)
t.to_csv(f'{OUT}/mineral_localities_table.csv',index=False)
print("localities csv",len(t))
print(t.head(5).to_string())
