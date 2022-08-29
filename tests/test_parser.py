import pytest
from openpyxl import Workbook

from parser import Parser


@pytest.fixture()
def parser(example_schematic_workbook: Workbook) -> Parser:
    return Parser(workbook=example_schematic_workbook, schematic={})


class TestParser:

    def test_creation(self, example_schematic_workbook: Workbook) -> None:
        schematic = dict()
        parser = Parser(workbook=example_schematic_workbook, schematic=schematic)
        assert isinstance(parser.workbook, Workbook)

    @pytest.mark.parametrize(
        'sheet_title, devices_quantity', [('1,0', 56), ('1,5', 56), ('2,5', 9), ('4,0', 1), ('6,0', 3)]
    )
    def test_load_sheet_contents(self, parser, sheet_title, devices_quantity):
        parser._load_sheet_contents(sheet_title)
        parsed_sheet = parser.raw_schematic[sheet_title]
        assert len(parsed_sheet) == devices_quantity

    # FIXME: add tests

    def test_parse_devices(self, parser):
        pass

    def test_parse(self, parser):
        parser.parse()
