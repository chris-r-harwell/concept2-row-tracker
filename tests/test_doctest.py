import doctest

import analyze_rowing
import concept2_downloader


def test_analyze_rowing_doctests():
    failures, tests_run = doctest.testmod(analyze_rowing, verbose=False)
    assert failures == 0
    assert tests_run > 0


def test_concept2_downloader_doctests():
    failures, tests_run = doctest.testmod(concept2_downloader, verbose=False)
    assert failures == 0
    assert tests_run > 0