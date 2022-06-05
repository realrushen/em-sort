# coding=utf-8
from pathlib import Path
from typing import Optional, Union, List, Dict

from openpyxl import Workbook
from openpyxl.styles import PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from entities import Device, Marker, Wire
from exceptions import UnsupportedTypeException, SheetDoesNotExistsException
from utils import pairwise


class Sorter:
    # FIXME: make loading this constants from settings
    INPUT_DATA_COLUMN = 'A'

    def __init__(self, workbook: Optional[Workbook] = None):
        self._input_wb = workbook
        self._output_wb = Workbook()
        self._sheets_for_sort: List[Worksheet] = []

    def add_sheets(self, sheets_names: List[str]) -> List[Worksheet]:
        for name in sheets_names:
            try:
                self._sheets_for_sort.append(self.wb[name])
            except KeyError:
                raise SheetDoesNotExistsException(f'Worksheet {name} does not exist.')
        return self._sheets_for_sort

    @property
    def wb(self) -> Optional[Workbook]:
        return self._input_wb

    @wb.setter
    def wb(self, workbook: Workbook) -> None:
        if isinstance(workbook, Workbook):
            self._input_wb = workbook
        else:
            raise UnsupportedTypeException

    def sort(self) -> Dict[str, List[Device]]:
        sorted_circuitry = {}
        for sheet in self._sheets_for_sort:
            wire_section = sheet.title
            devices_raw_markers = self._load_sheet_contents(sheet)
            parsed_devices = self._parse_devices(devices_raw_markers)
            sorted_devices = [device.sort() for device in parsed_devices]
            sorted_circuitry[wire_section] = sorted_devices
        return sorted_circuitry

    @staticmethod
    def _parse_devices(devices: Dict[str, List[str]]) -> List[Device]:
        parsed_devices = []

        for device_name, markers in devices.items():
            # ensure that device has valid markers quantity
            assert len(markers) % 2 == 0
            d = Device(name=device_name)

            for marker_from, marker_to in pairwise(markers):
                marker_from = Marker(marker_from).parse()
                marker_to = Marker(marker_to).parse()
                wire = Wire(frm=marker_from, to=marker_to)
                d.add_wires([wire])

            parsed_devices.append(d)
        return parsed_devices

    @staticmethod
    def _load_sheet_contents(worksheet: Worksheet, column: str = INPUT_DATA_COLUMN) -> Dict[str, List[str]]:
        devices_in_sheet = {}
        current_device = None

        for cell in worksheet[column]:
            if 'Device' in cell.value:
                current_device = cell.value
                devices_in_sheet[current_device] = []
                continue
            devices_in_sheet[current_device].append(cell.value)

        return devices_in_sheet

    def dump_circuitry(self, circuitry: Dict[str, List[Device]]) -> None:
        for wire_section, devices in circuitry.items():
            ws = self._output_wb.create_sheet(wire_section)
            self._write_markers(worksheet=ws, devices=devices)

        try:
            del self._output_wb['Sheet']  # delete created by default sheet if exists
        except KeyError:
            pass

    def save_to_file(self, file_path: Path) -> None:
        filename = f'{file_path.stem}_sorted{file_path.suffix}'
        self._output_wb.save(filename)

    def reset(self, workbook: Optional[Workbook] = None) -> None:
        """Resets object to empty state"""
        self._input_wb = workbook
        self._output_wb = Workbook()
        self._sheets_for_sort.clear()

    @staticmethod
    def _write_markers(worksheet: Worksheet, devices: List[Device], column: int = 1) -> None:
        row = 1
        for device in devices:
            device_sell = worksheet.cell(row=row, column=column, value=device.name)
            device_sell.fill = PatternFill(fill_type='solid', start_color='00C0C0C0', end_color='00C0C0C0')
            row += 1
            for marker in device.markers:
                worksheet.cell(row=row, column=column, value=marker.label)
                row += 1
