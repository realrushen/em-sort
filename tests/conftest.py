from pathlib import Path

import openpyxl
import pytest

TEST_DATA_FOLDER = Path().cwd() / 'testdata'


@pytest.fixture
def clean_workbook():
    return openpyxl.Workbook()


@pytest.fixture
def example_schematic_workbook():
    return openpyxl.load_workbook(TEST_DATA_FOLDER / 'schematic1.xlsx')


@pytest.fixture
def sorted_example_schematic_workbook():
    return openpyxl.load_workbook(TEST_DATA_FOLDER / 'schematic1_sorted.xlsx')
