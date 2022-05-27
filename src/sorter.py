from pathlib import Path
from typing import Optional, Union

import openpyxl
from openpyxl import Workbook
from openpyxl.styles import PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from entities import Device, Marker, Wire
from exceptions import UnsupportedTypeException
from utils import pairwise


class Sorter:
    # FIXME: make loading this constants from settings
    INPUT_DATA_COLUMN = 'A'

    def __init__(self, workbook: Optional[Workbook] = None):
        self._input_wb = workbook
        self._output_wb = Workbook()
        self._sheets_for_sort: list[Worksheet] = []

    def add_sheets(self, sheets_names: list[str]):
        for name in sheets_names:
            self._sheets_for_sort.append(self.wb[name])
        return self._sheets_for_sort

    @property
    def wb(self):
        return self._input_wb

    @wb.setter
    def wb(self, workbook: Union[Workbook, str, Path]):
        if isinstance(workbook, str):
            file_path = Path(workbook)
            wb = openpyxl.load_workbook(file_path)
        elif isinstance(workbook, Path):
            wb = openpyxl.load_workbook(workbook)
        elif isinstance(workbook, Workbook):
            wb = workbook
        else:
            raise UnsupportedTypeException
        self._input_wb = wb

    def sort(self):
        sorted_circuitry = {}
        for sheet in self._sheets_for_sort:
            wire_section = sheet.title
            devices_raw_markers = self._load_sheet_contents(sheet)
            parsed_devices = self._parse_devices(devices_raw_markers)
            sorted_devices = [device.sort() for device in parsed_devices]
            sorted_circuitry[wire_section] = sorted_devices
        return sorted_circuitry

    def _parse_devices(self, devices: dict):
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

    def _load_sheet_contents(self, worksheet: Worksheet, column: str = INPUT_DATA_COLUMN):
        devices_in_sheet = {}
        current_device = None

        for cell in worksheet[column]:
            if 'Device' in cell.value:
                current_device = cell.value
                devices_in_sheet[current_device] = []
            else:
                devices_in_sheet[current_device].append(cell.value)
        return devices_in_sheet

    def dump_circuitry(self, circuitry: dict):
        for wire_section, devices in circuitry.items():
            ws = self._output_wb.create_sheet(wire_section)
            self._write_markers(worksheet=ws, devices=devices)

        del self._output_wb['Sheet']  # delete created by default sheet

    def save_to_file(self, file_path: Path):
        filename = f'{file_path.stem}_sorted{file_path.suffix}'
        self._output_wb.save(filename)

    def reset(self, workbook: Workbook = None):
        self._input_wb = workbook
        self._output_wb = Workbook()
        self._sheets_for_sort: list[Worksheet] = []

    def _write_markers(self, worksheet: Worksheet, devices: list[Device], column: int = 1):
        row = 1
        for device in devices:
            device_sell = worksheet.cell(row=row, column=column, value=device.name)
            device_sell.fill = PatternFill(fill_type='solid', start_color='00C0C0C0', end_color='00C0C0C0')
            row += 1
            for marker in device.markers():
                worksheet.cell(row=row, column=column, value=marker.label)
                row += 1
