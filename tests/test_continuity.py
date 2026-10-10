import unittest
import sys
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from continuity import repair_annotation_bands, connected_bodies
from geometry import fill_labels

class ContinuityTests(unittest.TestCase):
    def setUp(self): self.canon=np.arange(96,dtype=np.uint8)
    def repair(self,a,seeds,band,water=None,gap=24):
        return repair_annotation_bands(a,seeds,band,np.ones(a.shape,bool),
                    np.zeros(a.shape,bool) if water is None else water,self.canon,gap)
    def test_black_road_crossing_one_feature_does_not_split(self):
        seeds=np.ones((45,60),np.uint8);seeds[:,27:34]=0;seeds[15:21,:]=0
        a=fill_labels(seeds,np.ones(seeds.shape,bool))
        ids,_=connected_bodies(a,self.canon)
        self.assertEqual(ids.max(),1)
    def test_false_halo_band_rejoins_identical_opposing_color(self):
        a=np.ones((40,50),np.uint8);a[:,23:28]=2
        seeds=a.copy();seeds[:,23:28]=0;band=seeds==0
        fixed,changed,_=self.repair(a,seeds,band)
        self.assertTrue(np.all(fixed==1));self.assertEqual(changed.sum(),200)
        self.assertEqual(connected_bodies(fixed,self.canon)[0].max(),1)
    def test_different_geology_on_opposite_sides_not_joined(self):
        a=np.ones((20,40),np.uint8);a[:,21:]=2;a[:,18:21]=3
        s=a.copy();s[:,18:21]=0
        fixed,changed,_=self.repair(a,s,s==0)
        np.testing.assert_array_equal(a,fixed);self.assertFalse(changed.any())
    def test_separate_same_color_bodies_stay_separate(self):
        a=np.ones((30,40),np.uint8);a[:,18:23]=2
        ids,_=connected_bodies(a,self.canon)
        self.assertNotEqual(ids[15,5],ids[15,35])
        self.assertEqual(ids.max(),3)
    def test_genuine_thin_unit_with_reliable_seed_is_not_removed(self):
        a=np.ones((20,40),np.uint8);a[:,19:21]=2
        fixed,changed,_=self.repair(a,a.copy(),np.ones(a.shape,bool))
        np.testing.assert_array_equal(a,fixed);self.assertFalse(changed.any())
    def test_water_stays_between_same_color_land(self):
        a=np.ones((20,40),np.uint8);a[:,18:22]=95
        s=a.copy();s[:,18:22]=0;water=a==95
        fixed,changed,_=self.repair(a,s,s==0,water)
        np.testing.assert_array_equal(a,fixed);self.assertFalse(changed.any())
    def test_long_unsupported_band_not_bridged(self):
        a=np.ones((20,80),np.uint8);a[:,20:60]=2;s=a.copy();s[:,20:60]=0
        fixed,changed,_=self.repair(a,s,s==0)
        np.testing.assert_array_equal(a,fixed);self.assertFalse(changed.any())
    def test_background_not_bridged(self):
        a=np.ones((20,40),np.uint8);a[:,18:22]=0;s=a.copy();mask=a>0
        fixed,changed,_=repair_annotation_bands(a,s,a==0,mask,np.zeros(a.shape,bool),self.canon)
        np.testing.assert_array_equal(a,fixed);self.assertFalse(changed.any())
    def test_competing_crossing_evidence_is_not_forced(self):
        a=np.ones((9,9),np.uint8)*3;s=np.zeros_like(a);band=np.zeros(a.shape,bool)
        band[4,:]=True;band[:,4]=True
        band[4,0]=band[4,-1]=band[0,4]=band[-1,4]=False
        s[4,0]=s[4,-1]=1;s[0,4]=s[-1,4]=2
        fixed,changed,conflict=self.repair(a,s,band)
        self.assertTrue(conflict[4,4]);self.assertFalse(changed[4,4]);self.assertEqual(fixed[4,4],3)
    def test_repair_cannot_split_another_body(self):
        a=np.ones((30,40),np.uint8);a[:,18:22]=2
        seeds=a.copy();seeds[12:17,18:22]=0;band=seeds==0
        fixed,changed,_=self.repair(a,seeds,band)
        np.testing.assert_array_equal(a,fixed);self.assertFalse(changed.any())
    def test_no_recoloring_when_target_already_connected_around_band(self):
        a=np.ones((30,40),np.uint8);a[8:22,18:22]=2
        seeds=a.copy();seeds[8:22,18:22]=0;band=seeds==0
        fixed,changed,_=self.repair(a,seeds,band)
        np.testing.assert_array_equal(a,fixed);self.assertFalse(changed.any())
    def test_palette_equivalence_not_global_dissolve(self):
        self.canon[2]=1;a=np.ones((12,20),np.uint8);a[:,7:12]=3;a[:,12:]=2
        ids,_=connected_bodies(a,self.canon)
        self.assertEqual(ids.max(),3);self.assertNotEqual(ids[5,2],ids[5,15])
if __name__=='__main__': unittest.main()
