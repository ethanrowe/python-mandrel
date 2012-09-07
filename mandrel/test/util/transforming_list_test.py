import unittest
import mock
import itertools
from mandrel import util

_trans_count = itertools.count(0)

def mock_transform():
    t = mock.Mock(name='MockTransform%d' % _trans_count.next())
    t.side_effect = lambda v: v.transformed
    return t

_vals_count = itertools.count(0)

def mock_value():
    return mock.Mock(name='MockValue%d' % _vals_count.next())

class TestTransformingList(unittest.TestCase):
    def testAppendBasics(self):
        t = mock_transform()
        l = util.TransformingList(t)
        self.assertEqual(0, len(l))
        self.assertEqual((), tuple(l))
        a = mock_value()
        b = mock_value()
        l.append(a)
        self.assertEqual(1, len(l))
        self.assertEqual((a.transformed,), tuple(l))
        l.append(b)
        self.assertEqual(2, len(l))
        self.assertEqual((a.transformed, b.transformed), tuple(l))

    def testAccessBasics(self):
        t = mock_transform()
        l = util.TransformingList(t)
        vals = [mock_value() for i in xrange(5)]
        l[0:3] = vals[0:3]
        self.assertEqual(3, len(l))
        self.assertEqual(tuple(v.transformed for v in vals[0:3]), tuple(l))
        self.assertEqual(2, len(l[1:3]))
        self.assertEqual((vals[1].transformed, vals[2].transformed), tuple(l[1:3]))
        l[1] = vals[3]
        l[0] = vals[4]
        self.assertEqual(3, len(l))
        self.assertEqual((vals[4].transformed, vals[3].transformed), (l[0], l[1]))
        del l[0:2]
        self.assertEqual(1, len(l))
        self.assertEqual(vals[2].transformed, l[0])
        del l[0]
        self.assertEqual(0, len(l))

    def testExtend(self):
        t = mock_transform()
        vals = [mock_value() for i in xrange(5)]
        exp = tuple(v.transformed for v in vals)
        l = util.TransformingList(t)
        l.extend(vals)
        self.assertEqual(exp, tuple(l))
        l = util.TransformingList(t)
        v = mock_value()
        l.append(v)
        l.extend(vals)
        self.assertEqual((v.transformed,) + exp, tuple(l))

    def testInsertPop(self):
        t = mock_transform()
        a, b, c = (mock_value() for i in xrange(3))
        l = util.TransformingList(t)
        l.append(a)
        l.append(b)
        l.insert(1, c)
        self.assertEqual((a.transformed, c.transformed, b.transformed), tuple(l))

        r = l.pop(0)
        self.assertEqual((c.transformed, b.transformed), tuple(l))
        self.assertEqual(a.transformed, r)

    def testContainment(self):
        t = mock_transform()
        vals = [mock_value() for i in xrange(5)]
        l = util.TransformingList(t)
        member = lambda v: v in l
        self.assertFalse(member(vals[0]))
        l.extend(vals[0:4])
        self.assertTrue(member(vals[0]))
        self.assertFalse(member(vals[4]))

        l.append(vals[2])
        self.assertEqual(0, l.count(vals[4]))
        self.assertEqual(1, l.count(vals[1]))
        self.assertEqual(2, l.count(vals[2]))

