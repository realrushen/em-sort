# coding=utf-8
import os
import sys
from typing import TypeVar, Iterable, List
import functools
import operator

T = TypeVar('T')


def pairwise(iterable: Iterable[T]):
    """ s -> (s0, s1), (s2, s3), (s4, s5), ... """
    a = iter(iterable)
    return zip(a, a)


def resource_path(relative_path: str):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def flatten_list(lst: List[List[T]]) -> List[T]:
    """ Flattens list of lists """
    return functools.reduce(operator.iconcat, lst, [])
