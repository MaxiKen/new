import json
# ---- Picture 2 (NGSA 2004) legend: 92 printed rows, 86 distinct labels ----
P2_ROWS = [
 (1,'Al','Alluvium'),(2,'MWS','Sands,Gravels and Clay'),(3,'AB','Sands and Pebbles'),
 (4,'MS','Sand, Clay and Mangrove Swamps'),(5,'SDsm','Sand,Clay and Swamp'),
 (6,'Cst','Sands, Clays, siltstones and limestones'),(7,'Bnst','Sand and Clay'),
 (8,'b','Younger Basalt'),(9,'bb','Basalt'),(10,'OAlgs','Lignite,Claystone and shale'),
 (11,'Issh','Clay clayey sands and shale'),(12,'Gwss','Sandstone and Clay'),
 (13,'Glcl','Sandstones and Clays'),(14,'Wss','Sandstone and Clay'),(15,'Esh','Shale and limestone'),
 (16,'Imsh','Clay and Shale with Limestone Intercalations'),(17,'Kss','Sandstone,shale and Clay'),
 (18,'Dsh','Shale'),(19,'Kls','Limestone'),(20,'Gss','Sandstone,Siltstone,Shale and ironstone'),
 (21,'Ajst','False - bedded sandstone'),(22,'Ncsh','Coal, shale and sandstone'),
 (23,'Ncsh','Sandstone, limestone, Coal'),(24,'Asl','Sandstone and Limestone'),
 (25,'Mcst','Coal,Sandstone and Shale'),(26,'Bssf','Sandstone and Ironstone'),(27,'Nsh','Shale and mudstone'),
 (28,'ANsh','Shale and Limestone'),(29,'Tst','Sandstone, siltstone and shale'),(30,'Glls','Limestone'),
 (31,'Wss','Sandstone, clays and shale'),(32,'Wcs','Clays and loose sandstone'),
 (33,'Wsh','Shale (Phosphate nodules)'),(34,'Ts','Siltstone and Sandstone'),
 (35,'Psh','Shale,limestone and sandstone'),(36,'Lass','Sandstone,shale and sandyshale'),
 (37,'NPss','Feldspathic sandstone and siltstone'),(38,'Glpg','Pebbles and grit'),
 (39,'Glss','Clay grit and pebbles'),(40,'Glgss','Gravel and sand'),
 (41,'Fsh','Blackshale, siltstone and sandstone'),(42,'Ess','Sandstone'),
 (43,'Esh','Blackshale, siltstone and sandstone'),(44,'Mlst','Limestone and Siltstone'),
 (45,'Awst','Sandstone'),(46,'Yls','Shale, sandyclay, calcerous sandstones'),
 (47,'Bss','Feldspathic sandstone calcerous sandstone and shelly limestone'),
 (48,'Arlsh','Shale and limestone with sandstone intercalations'),
 (49,'MyP','Quartz porphyry'),(50,'MyG','Granite and granite porphery'),(51,'Myl','Ignimbrite'),
 (52,'Mys','Syenite, quartz-syenite and gabbro'),(53,'MGp','Granites and granite porphyry'),
 (54,'MyP','Porphyry / quartz porphyry'),(55,'r','Rhyolite'),(56,'Jyr','Rhyolite'),
 (57,'JyG','Biotite granite'),(58,'JyA','Trachy- andesine'),(59,'P','Pegmatite'),(60,'D','Dolerite'),
 (61,'ODh','Bauchite quartz- diorite'),(62,'OGd','Biotite and biotite hornblende granodiorite'),
 (63,'OGS','Syenite,mainly of pyroxene diorite composition'),
 (64,'OSq','Coarse biotite and biotite muscovite granite'),(65,'OGh','Coarse hornblende granite'),
 (66,'OGf','Fine-grained biotite granite'),(67,'OGm','Medium-to coarse-grained biotite granite'),
 (68,'OGu','Undifferentiated granite,migmatite and granite Gneiss'),(69,'OGCh','Charnockitic rocks'),
 (70,'OGr','Gabbro and quartz gabbro'),(71,'MV','Meta Volcanic Meta Sedimentary including pebbly schist'),
 (72,'Sa','Amphibole Schist,Amphibolite'),(73,'BIF','Banded Iron Formation'),
 (74,'Sp','Slate phylite and meta siltstone, locally hornfelstic / carbonaceous'),(75,'m','Marble'),
 (76,'Sf','Fine-grained flaggy quartzite and Quartz Schist.'),
 (77,'Qs','Quartzite, massive and schistose, also occuring as ridges'),
 (78,'MS','Pelitic Schist / Muscovite Schist'),(79,'Su','Undifferentiated schists,including phyllities.'),
 (80,'Mc','Meta-conglomerate'),(81,'bS','Biotite Garnet Gneiss Schist'),(82,'bG-h','Biotite hornblende gneiss'),
 (83,'OPg','Porphyroblastic Gneiss'),(84,'GG','Granite Gneiss'),(85,'Ge','Granulite and gneiss'),
 (86,'bG','Banded gneiss / biotite gneiss'),(87,'MaG','Migmatitic augen gneiss'),(88,'MG','Migmatitic gneiss'),
 (89,'M','Migmatite'),(90,'qs','Silicified, sheared rocks, large quartz veins'),(91,'My','Mylonites'),
 (92,'aMy','Mylonites interlayered with amphibolites'),
]
# ---- Picture 1 legend: 86 entries in order TR_left(20), TR_right(15), BOT_left(17), BOT_mid(17), BOT_right(17)
P1_LABELS = [
 'Ignimbrite','Lignite, Claystone and shale','Limestone','Marble','Medium-to coarse-Grained Biotite granite',
 'Meta Volcanic Meta Sedimentary including pebbly schist','Meta-conglomerate','Migmatite','Migmatitic Gneiss',
 'Migmatitic augen Gneiss','Mylonites','Mylonites interlayened with Amphibolites','Pebbles and Grit','Pegmatite',
 'Pelitic Schist/Muscovite Schist','Porphyritic Granite/Coarse porphyritic biotite and biotite hornblende granite',
 'Porphyry/Quartz Porphyry','Quartz feldspathic granulite and gneiss','Quartz porphyry',
 'Quartzite, massive and schistose, also occuring as ridges',
 'Rhyolite','Sand and Clay','Sand, Clay and Swamp','Sands and Pebbles','Sands, Clays, Siltstones and limestones',
 'Sands, Gravels and Clay','Sandstone','Sandstone and Clay','Sandstone and Ironstone','Sandstone and Limestone',
 'Sandstone, Limestone, Coal','Sandstone, Siltstone and Shale','Sandstone, Siltstone, Shale and Ironstone',
 'Sandstone, shale and clay','Sandstone, shale and sandyshale',
 'Alluvium','Amphibole Schist, Amphibolite','Banded Gneiss/Biotite Gneiss','Banded Iron Formation','Basalt',
 'Biotite Garnet Gneiss Schist','Biotite Granite','Biotite Hornblende Gneiss',
 'Biotite and biotite Hornblende granodiorite','Black shale, siltstone and sandstone','Blackshale, Siltstone and Sandstone',
 'Charnockitic Rocks','Clay Grit and Pebbles','Clay and Shale with Limestone Intercalations',
 'Clay clayey sands and shale','Clay, Clayey Sands and Shale','Clays and loose sandstone',
 'Coal candstone and shale','Coal, Sandstone and Shale','Coal, Shale and Sandstone',
 'Coarse Porphyritic homblende granite','Coarse porphyritic porphyroblastic mica granite',
 'Coarse, Porphyritic biotite and biotite muscovite granite','Dolerite','False - Bedded Sandstone',
 'Feldspathic sandstone and siltstone','Feldspathic sandstone calcerous sandstone and shelly limestone',
 'Fine-grained biotite granite','Fine-grained flaggy quartzite and Quartz Schist',
 'Gabbro and quartz gabbro and meta intrusives','Granite Gneiss','Granite and Granite Porphery','Gravel and Sand',
 'Hypersthene quartz-diorite',
 'Sandstones and Clays','Sandstones, Clays and Shale','Shale (Phosphate nodules)','Shale and Limestone',
 'Shale and Limestone with Sandstone Intercalations','Shale and Mudstone','Shale, Limestone and Sandstone',
 'Shale, Sandclay, Calcerous sandstones','Silicified, sheared rocks, large quartz veins',
 'Slate phylite and meta siltstone, locally hornfelstic/carbonaceous','Syenite, Quartz-Syenite and Gabbro',
 'Syenite, mainly of Pyroxenen Diorite composition','Trachy - andesine',
 'Undifferentiated Schists, including Phyllites','Undifferentiated Migmatite and granite, Gneiss porphyroblastic',
 'Younger Basalt','porphroblastic Gneiss',
]
# Row-level crosswalk: picture-2 row -> picture-1 entry number (1-based), None = no picture-1 counterpart
P2_TO_P1 = {1:36,2:26,3:24,4:23,5:23,6:25,7:22,8:85,9:40,10:2,11:50,12:28,13:70,14:28,15:73,16:49,17:34,
 18:None,19:3,20:33,21:60,22:55,23:31,24:30,25:54,26:29,27:75,28:73,29:32,30:3,31:71,32:52,33:72,34:None,
 35:76,36:35,37:61,38:13,39:48,40:68,41:46,42:27,43:46,44:None,45:27,46:77,47:62,48:74,
 49:19,50:67,51:1,52:80,53:67,54:17,55:21,56:21,57:42,58:82,59:14,60:59,61:None,62:44,63:81,64:58,65:56,
 66:63,67:5,68:84,69:47,70:65,71:6,72:37,73:39,74:79,75:4,76:64,77:20,78:15,79:83,80:7,81:41,82:43,83:86,
 84:66,85:18,86:38,87:10,88:9,89:8,90:78,91:11,92:12}

def load_colors():
    a = json.load(open('/home/user/work/p1_swatches.json'))
    p1 = []
    for k in ['TR_left', 'TR_right', 'BOT_left', 'BOT_mid', 'BOT_right']:
        p1 += [tuple(s['rgb']) for s in a[k]]
    b = json.load(open('/home/user/work/p2_swatches_raw.json'))
    p2 = [tuple(s['rgb']) for s in b]
    return p2, p1

def norm_label(s):
    return ' '.join(s.replace(',', ', ').split()).lower().replace(' ,', ',')

if __name__ == '__main__':
    p2c, p1c = load_colors()
    print('P2 rows', len(P2_ROWS), 'colors', len(p2c))
    print('P1 labels', len(P1_LABELS), 'colors', len(p1c))
    labels = {}
    for r, c, l in P2_ROWS:
        labels.setdefault(norm_label(l), []).append(r)
    dups = {k: v for k, v in labels.items() if len(v) > 1}
    print('distinct P2 labels (normalised):', len(labels))
    print('duplicate labels:', dups)
    used = set(v for v in P2_TO_P1.values() if v)
    print('P1 entries used by crosswalk:', len(used))
    print('P1 entries NOT used:', [ (i+1, P1_LABELS[i]) for i in range(len(P1_LABELS)) if (i+1) not in used])
    print('P2 rows without P1 counterpart:', [r for r,_,_ in P2_ROWS if P2_TO_P1.get(r) is None])
