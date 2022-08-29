from typing import Dict, List

from openpyxl import Workbook

from entities import Device, Marker, Wire
from exceptions import UnsupportedMarkerFormatException
from utils import pairwise


class Parser:
    INPUT_DATA_COLUMN = 'A'
    SUPPORTED_WIRE_SECTIONS = ('1,0', '1,5', '2,5', '4,0', '6,0')

    def __init__(self, workbook: Workbook, schematic: Dict[str, List[Device]]):
        self.parsed_schematic = schematic
        self.raw_schematic = {}
        self.workbook = workbook

    def _load_sheet_contents(self, sheet_title: str, column: str = INPUT_DATA_COLUMN) -> None:
        raw_devices = {}
        current_device = None

        for cell in self.workbook[sheet_title][column]:
            if 'Device' in cell.value:
                current_device = cell.value
                raw_devices[current_device] = []
                continue
            raw_devices[current_device].append(cell.value)

        self.raw_schematic[sheet_title] = raw_devices

    def _parse_devices(self, devices: Dict[str, List[str]], wire_section: str) -> List[Device]:
        parsed_devices = []

        for device_name, markers in devices.items():
            # ensure that device has valid markers quantity
            assert len(markers) % 2 == 0
            d = Device(name=device_name)

            for marker_from, marker_to in pairwise(markers):
                marker_from, marker_to = Marker(marker_from), Marker(marker_to)

                for marker in (marker_from, marker_to):
                    try:
                        marker.parse()
                    except UnsupportedMarkerFormatException:
                        print(f'Unsupported format for marker: {repr(marker.label)}')  # FIXME: add logging

                wire = Wire(frm=marker_from, to=marker_to, section=wire_section)
                d.add_wires([wire])

            parsed_devices.append(d)
        return parsed_devices

    def parse(self) -> None:
        for sheet in self.workbook.worksheets:
            wire_section: str = sheet.title
            if wire_section not in Parser.SUPPORTED_WIRE_SECTIONS:
                continue
            self._load_sheet_contents(wire_section)
            parsed_devices = self._parse_devices(self.raw_schematic[wire_section], wire_section)
            self.parsed_schematic[wire_section] = parsed_devices
