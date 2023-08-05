""" Utility functions to process the identifiers of tests. """

import re

from .constants import MARKER_NAME, MARKER_KWARG_ID, MARKER_KWARG_DEPENDENCIES


REGEX_PARAMETERS = re.compile(r"\[.+\]$")


def clean_nodeid(nodeid):
    """
    Remove any superfluous ::() from a node id.

    >>> clean_nodeid('test_file.py::TestClass::()::test')
    'test_file.py::TestClass::test'
    >>> clean_nodeid('test_file.py::TestClass::test')
    'test_file.py::TestClass::test'
    >>> clean_nodeid('test_file.py::test')
    'test_file.py::test'
    """
    return nodeid.replace("::()::", "::")


def strip_nodeid_parameters(nodeid):
    """
    Strip parameters from a node id.

    >>> strip_nodeid_parameters('test_file.py::TestClass::test[foo]')
    'test_file.py::TestClass::test'
    >>> strip_nodeid_parameters('test_file.py::TestClass::test')
    'test_file.py::TestClass::test'
    """
    return REGEX_PARAMETERS.sub("", nodeid)


def get_absolute_nodeid(nodeid, scope):
    """
    Transform a possibly relative node id to an absolute one using the scope in which it is used.

    >>> scope = 'test_file.py::TestClass::test'
    >>> get_absolute_nodeid('test2', scope)
    'test_file.py::TestClass::test2'
    >>> get_absolute_nodeid('TestClass2::test2', scope)
    'test_file.py::TestClass2::test2'
    >>> get_absolute_nodeid('test_file2.py::TestClass2::test2', scope)
    'test_file2.py::TestClass2::test2'
    """
    parts = nodeid.split("::")
    # Completely relative (test_name), so add the full current scope (either file::class or file)
    if len(parts) == 1:
        base_nodeid = scope.rsplit("::", 1)[0]
        nodeid = f"{base_nodeid}::{nodeid}"
    # Contains some scope already (Class::test_name), so only add the current file scope
    elif "." not in parts[0]:
        base_nodeid = scope.split("::", 1)[0]
        nodeid = f"{base_nodeid}::{nodeid}"
    return clean_nodeid(nodeid)


def get_names(item):
    """
    Get all names for a test.

    This will use the following methods to determine the name of the test:
        - If given, the custom name(s) passed to the keyword argument name on the marker
    """
    names = set()

    # Custom name
    markers = get_markers(item, MARKER_NAME)
    for marker in markers:
        if MARKER_KWARG_ID in marker.kwargs:
            names.add(marker.kwargs[MARKER_KWARG_ID])

    return names


def get_markers(item, name):
    """Get all markers with the given name for a given item."""
    for marker in item.iter_markers():
        if marker.name == name:
            yield marker


def as_list(lst):
    """
    Convert the input to a list of strings.

    If the input is a single string, it will be wrapped in a list instead of iterated over.

    >>> as_list(['foo'])
    ['foo']
    >>> as_list('foo')
    ['foo']
    """
    return lst
