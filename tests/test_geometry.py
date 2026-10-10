import unittest
import sys
from pathlib import Path
import numpy as np
import shapely as sh
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from geometry import fill_labels, no_black_palette, smooth_samples, validate_coverage

class GeometryTests(unittest.TestCase):
    def test_black_band_split_is_centered(self):
        for width in range(1,21):
            seeds=np.zeros((7,width+20),np.int32);seeds[:,:10]=1;seeds[:,10+width:]=2
            filled=fill_labels(seeds,np.ones(seeds.shape,bool))
            edge=np.flatnonzero(np.diff(filled[3])!=0)[0]+1
            self.assertLessEqual(abs(edge-(10+width/2)),.5)
            self.assertTrue(np.all(filled>0))

    def test_footprint_limits_fill(self):
        seed=np.zeros((9,9),np.int32);seed[4,4]=3
        mask=np.zeros(seed.shape,bool);mask[2:7,2:7]=1
        filled=fill_labels(seed,mask)
        self.assertTrue(np.all(filled[mask]==3));self.assertTrue(np.all(filled[~mask]==0))

    def test_no_seeds_is_explicit_error(self):
        with self.assertRaises(ValueError):fill_labels(np.zeros((4,4)),np.ones((4,4),bool))

    def test_black_and_near_black_are_rejected(self):
        self.assertFalse(no_black_palette(['#000000']))
        self.assertFalse(no_black_palette(['#101010']))
        self.assertTrue(no_black_palette(['#99d8eb','#dd00fe','#9b9b9b']))

    def test_shared_coverage(self):
        p=np.array([sh.box(0,0,1,1),sh.box(1,0,2,1)],object)
        self.assertAlmostEqual(validate_coverage(p).area,2)

    def test_internal_hole_fails(self):
        p=sh.Polygon([(0,0),(5,0),(5,5),(0,5)],holes=[[(1,1),(1,2),(2,2),(2,1)]])
        with self.assertRaises(AssertionError):validate_coverage(np.array([p],object))

    def test_smoothing_preserves_junctions(self):
        a=np.array([[0.,0.],[1,0],[1,1],[2,1],[2,2],[3,2]])
        b=smooth_samples(a,1,False)
        np.testing.assert_equal(b[0],a[0]);np.testing.assert_equal(b[-1],a[-1])

    def test_closed_smoothing_keeps_closed_ring(self):
        a=np.array([[0.,0.],[2,0],[2,2],[0,2],[0,0]])
        b=smooth_samples(a,.5,True)
        np.testing.assert_equal(b[0],b[-1])

if __name__=='__main__':unittest.main()
