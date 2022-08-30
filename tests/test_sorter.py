import openpyxl
import pytest

from exceptions import SheetDoesNotExistsException
from sorter import Sorter


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
def expected_sorted_schematic(wire_sections_for_sort, sorted_example_schematic_workbook):
    sorter = Sorter(workbook=sorted_example_schematic_workbook)
    sorter.add_sheets(wire_sections_for_sort)

    sorter.sort()
    return sorter.schematic


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
            assert isinstance(sheet, str)

    def test_add_sheets_raises_exception(self, sorter_with_test_data):
        with pytest.raises(SheetDoesNotExistsException):
            sorter_with_test_data.add_sheets(['1,0', '1,5', 4])

    def test_dump_circuitry(self, expected_sorted_schematic, sorter_with_test_data, wire_sections_for_sort):
        sorter_with_test_data.add_sheets(wire_sections_for_sort)
        sorter_with_test_data.sort()
        sorter_with_test_data.dump_circuitry()
        sorted_sheets = sorter_with_test_data._output_wb.sheetnames
        assert sorted_sheets == list(expected_sorted_schematic.keys())

        for wire_section in sorted_sheets:
            dumped_markers = list(map(lambda o: o[0], sorter_with_test_data._output_wb[wire_section].values))
            expected_dumped_markers = []
            for device in expected_sorted_schematic[wire_section]:
                expected_dumped_markers.append(device.name)
                for marker in device.markers:
                    expected_dumped_markers.append(marker)
            assert dumped_markers == expected_dumped_markers

    def test_sort(self, sorter_with_test_data, expected_sorted_schematic, wire_sections_for_sort):
        sorter_with_test_data.add_sheets(wire_sections_for_sort)
        sorter_with_test_data.sort()

        for wire_section in sorter_with_test_data.schematic.keys():
            sorted_devices = sorter_with_test_data.schematic[wire_section]
            expected_devices = expected_sorted_schematic[wire_section]
            assert len(sorted_devices) == len(expected_devices)

            for sorted_device, expected_device in zip(sorted_devices, expected_devices):
                assert sorted_device == expected_device

    def test_reset(self, sorter_with_test_data):
        empty_sorter = sorter_with_test_data.reset()
        assert empty_sorter._input_wb is None
        assert len(empty_sorter._output_wb.worksheets) == 0
        assert len(empty_sorter._sheets_for_sort) == 0

    def test_write_to_file(self, sorter_with_test_data, wire_sections_for_sort, tmp_path):
        sorter_with_test_data.add_sheets(wire_sections_for_sort)
        sorter_with_test_data.sort()
        sorter_with_test_data.dump_circuitry()

        save_path = tmp_path / 'out.xlsx'

        sorter_with_test_data.save_to_file(save_path, in_place=True)
        assert save_path.exists()
        assert save_path.is_file()

        sorter_with_test_data.save_to_file(save_path)
        save_path.with_name(f'{save_path.stem}_sorted')
        assert save_path.exists()
        assert save_path.is_file()
