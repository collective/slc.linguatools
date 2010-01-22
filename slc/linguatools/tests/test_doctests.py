import unittest
import doctest

from zope.testing import doctestunit
from zope.component import testing, eventtesting

from Testing import ZopeTestCase as ztc

from slc.linguatools.tests import base


def test_suite():
    return unittest.TestSuite([

        # Demonstrate the main content types
        # ztc.ZopeDocFileSuite(
        #     'README.txt', package='slc.linguatools',
        #     test_class=base.FunctionalTestCase,
        #     optionflags=doctest.REPORT_ONLY_FIRST_FAILURE |
        #         doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
        #
        # ztc.ZopeDocFileSuite(
        #     'tests/linguatest.txt', package='slc.linguatools',
        #     test_class=base.FunctionalTestCase,
        #     optionflags=doctest.REPORT_ONLY_FIRST_FAILURE |
        #         doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        ztc.ZopeDocFileSuite(
            'tests/lttest.txt', package='slc.linguatools',
            test_class=base.FunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE |
                doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
