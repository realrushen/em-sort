from pathlib import Path

import openpyxl
import pytest
from openpyxl.worksheet.worksheet import Worksheet

from exceptions import SheetDoesNotExistsException
from sorter import Sorter

TEST_DATA_FOLDER = Path().cwd() / 'testdata'


@pytest.fixture
def clean_workbook():
    return openpyxl.Workbook()


@pytest.fixture
def example_schematic_workbook():
    return openpyxl.load_workbook(TEST_DATA_FOLDER / 'schematic1.xlsx')


@pytest.fixture
def wire_sections_for_sort():
    return ['1,0', '1,5', '2,5']


@pytest.fixture
def empty_sorter():
    return Sorter()


@pytest.fixture
def sorter_with_test_data(example_schematic_workbook, wire_sections_for_sort):
    sorter = Sorter(workbook=example_schematic_workbook)
    return sorter


@pytest.fixture
def expected_sorted_circuitry(wire_sections_for_sort):
    workbook = openpyxl.load_workbook(TEST_DATA_FOLDER / 'schematic1_sorted.xlsx')
    sorter = Sorter(workbook=workbook)
    sorter.add_sheets(wire_sections_for_sort)

    sorted_circuitry = {}
    for sheet in sorter._sheets_for_sort:
        wire_section = sheet.title
        devices_raw_markers = sorter._load_sheet_contents(sheet)
        parsed_devices = sorter._parse_devices(devices_raw_markers)
        sorted_circuitry[wire_section] = parsed_devices
    return sorted_circuitry


class TestSorter:
    def test_creation(self, example_schematic_workbook, empty_sorter):
        assert empty_sorter._input_wb is None
        assert isinstance(empty_sorter._output_wb, openpyxl.Workbook)
        assert isinstance(empty_sorter._sheets_for_sort, list)
        assert len(empty_sorter._sheets_for_sort) == 0

        sorter = Sorter(workbook=example_schematic_workbook)
        assert id(sorter._input_wb) == id(example_schematic_workbook)
        assert isinstance(sorter._output_wb, openpyxl.Workbook)
        assert isinstance(sorter._sheets_for_sort, list)
        assert len(sorter._sheets_for_sort) == 0

    def test_wb_property(self, empty_sorter, example_schematic_workbook):
        empty_sorter.wb = example_schematic_workbook
        assert id(empty_sorter.wb) == id(example_schematic_workbook)

    def test_add_sheets(self, sorter_with_test_data):
        sorter_with_test_data.add_sheets(['1,0', '1,5', '2,5'])
        assert len(sorter_with_test_data._sheets_for_sort) == 3

        for sheet in sorter_with_test_data._sheets_for_sort:
            assert isinstance(sheet, Worksheet)

    def test_add_sheets_raises_exception(self, sorter_with_test_data):
        with pytest.raises(SheetDoesNotExistsException):
            sorter_with_test_data.add_sheets(['1,0', '1,5', 4])

    def test_sort(self, sorter_with_test_data, expected_sorted_circuitry, wire_sections_for_sort):
        sorter_with_test_data.add_sheets(wire_sections_for_sort)
        sorted_circuitry = sorter_with_test_data.sort()
        for wire_section in wire_sections_for_sort:
            sorted_section = sorted_circuitry[wire_section]
            expected_sorted_section = expected_sorted_circuitry[wire_section]
            for sorted_device, expected_device in zip(sorted_section, expected_sorted_section):
                assert sorted_device == expected_device
