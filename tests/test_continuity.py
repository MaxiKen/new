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
    def test_untrusted_annotation_halo_inside_one_body_is_filled(self):
        a=np.ones((30,40),np.uint8);a[8:22,18:22]=2
        seeds=a.copy();seeds[8:22,18:22]=0;band=seeds==0
        fixed,changed,_=self.repair(a,seeds,band)
        self.assertTrue(changed.any());self.assertTrue(np.all(fixed==1))
    def test_palette_equivalence_not_global_dissolve(self):
        self.canon[2]=1;a=np.ones((12,20),np.uint8);a[:,7:12]=3;a[:,12:]=2
        ids,_=connected_bodies(a,self.canon)
        self.assertEqual(ids.max(),3);self.assertNotEqual(ids[5,2],ids[5,15])

class ObliqueContinuityTests(unittest.TestCase):
    setUp=ContinuityTests.setUp
    repair=ContinuityTests.repair
    def oblique(self, mirrored=False):
        y,x=np.indices((70,70))
        band=(x+y>=54)&(x+y<=84)  # 31 px axially, about 22 px normally
        a=np.ones(band.shape,np.uint8);a[band]=2
        seeds=a.copy();seeds[band]=0
        if mirrored:return a[:,::-1],seeds[:,::-1],band[:,::-1]
        return a,seeds,band
    def test_diagonal_annotation_band_rejoins(self):
        for mirrored in (False,True):
            a,seeds,band=self.oblique(mirrored)
            fixed,changed,_=self.repair(a,seeds,band)
            self.assertTrue(changed.any())
            ids,_=connected_bodies(fixed,self.canon)
            if mirrored:self.assertEqual(ids[0,-1],ids[-1,0])
            else:self.assertEqual(ids[0,0],ids[-1,-1])
            self.assertFalse(np.any(changed & ~band))
    def test_diagonal_repair_respects_physical_gap_limit(self):
        a,seeds,band=self.oblique()
        _,changed,_=self.repair(a,seeds,band,gap=15)
        self.assertFalse(changed.any())
    def test_diagonal_water_not_crossed(self):
        a,seeds,band=self.oblique();a[band]=95
        fixed,changed,_=self.repair(a,seeds,band,water=band)
        self.assertFalse(changed.any());np.testing.assert_array_equal(fixed,a)
    def test_oblique_other_reliable_geology_protected(self):
        a,seeds,band=self.oblique();seeds[35,35]=2
        fixed,changed,_=self.repair(a,seeds,band)
        self.assertEqual(fixed[35,35],2);self.assertFalse(changed[35,35])
        # Any source-evidenced donor component must remain connected.
        ids,_=connected_bodies(fixed,self.canon)
        self.assertEqual(len(np.unique(ids[fixed==2])),1)
    def test_turning_photo_does_not_change_diagonal_repair(self):
        a,seeds,band=self.oblique()
        fixed,_,_=self.repair(a,seeds,band)
        rotated,_,_=self.repair(np.rot90(a),np.rot90(seeds),np.rot90(band))
        np.testing.assert_array_equal(fixed,np.rot90(rotated,-1))

class VisiblePaintTests(unittest.TestCase):
    def test_thin_real_unit_without_eroded_core_blocks_join(self):
        a=np.ones((25,40),np.uint8);a[:,18:23]=2
        reliable=a.copy();reliable[:,18:23]=0
        observed=np.zeros_like(a);observed[:,20]=2
        fixed,changed,_=repair_annotation_bands(a,reliable,reliable==0,np.ones(a.shape,bool),
            np.zeros(a.shape,bool),np.arange(96,dtype=np.uint8),observed=observed)
        np.testing.assert_array_equal(fixed,a);self.assertFalse(changed.any())
    def test_real_enclosed_unit_not_deleted_as_halo(self):
        a=np.ones((25,40),np.uint8);a[7:17,18:23]=2
        reliable=a.copy();reliable[a==2]=0;observed=np.where(a==2,2,0).astype('uint8')
        fixed,changed,_=repair_annotation_bands(a,reliable,a==2,np.ones(a.shape,bool),
            np.zeros(a.shape,bool),np.arange(96,dtype=np.uint8),observed=observed)
        np.testing.assert_array_equal(fixed,a);self.assertFalse(changed.any())

if __name__=='__main__': unittest.main()
