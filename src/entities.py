# coding=utf-8
from typing import List, Tuple, Optional

from exceptions import UnsupportedMarkerFormatException, InvalidMarkersPairException


class Marker:
    # FIXME: make loading this constants from settings
    WIRE_SEP = ' '
    ADDRESS_SEP = ':'
    JACK_SEP = '-'

    def __init__(self, label: str):
        self.label = label
        self.wire_name: Optional[str] = None
        self.device: Optional[str] = None
        self.jack: Optional[str] = None
        self.contact: Optional[str] = None
        self.connection: Optional[str] = None
        self.unsupported_format = False

    def parse(self):
        """
        Valid label examples:
                                'X2:14:1 9'
                                'A1:X4-1 952'
                                'A1:GND2'
                                'PE:PE'
        """
        if self.label.count(self.WIRE_SEP) == 1:
            address, self.wire_name = self.label.split(self.WIRE_SEP)
        elif self.label.count(self.WIRE_SEP) == 0:
            address = self.label
        else:
            self.unsupported_format = True
            raise UnsupportedMarkerFormatException(f'Parsing failed on marker with label: {repr(self.label)}')

        if self.label.count(self.ADDRESS_SEP) == 1:
            self.device, self.contact = address.split(self.ADDRESS_SEP)
        elif self.label.count(self.ADDRESS_SEP) == 2:
            self.device, self.contact, self.connection = address.split(self.ADDRESS_SEP)
        else:
            self.unsupported_format = True
            raise UnsupportedMarkerFormatException

        if self.contact.count(self.JACK_SEP) == 1:
            self.jack, self.contact = self.contact.split(self.JACK_SEP)
            # check that self.jack and self.contact contains useful information
            if not self.jack or not self.contact:
                self.unsupported_format = True
                raise UnsupportedMarkerFormatException
        return self

    @property
    def address(self) -> str:
        if self.jack:
            address_params = [self.device, self.JACK_SEP.join([self.jack, self.contact])]
        else:
            address_params = [self.device, self.contact]

        if self.connection:
            address_params.append(self.connection)

        return self.ADDRESS_SEP.join(address_params)

    def __repr__(self) -> str:
        marker_repr = repr(self.label)
        return f'Marker(label={marker_repr})'

    def __str__(self) -> str:
        marker_data = [self.address]
        if self.wire_name:
            marker_data.append(self.wire_name)
        return self.WIRE_SEP.join(marker_data)

    def __hash__(self):
        return hash((self.label, self.wire_name, self.device, self.jack, self.contact, self.connection))

    def __eq__(self, other):
        try:
            return (self.label, self.wire_name, self.device, self.jack, self.contact, self.connection) \
                   == (other.label, other.wire_name, other.device, other.jack, other.contact, other.connection)
        except AttributeError:
            return NotImplemented


class Wire:
    """
    Container object for two markers.

    Wire can connect two different devices with different or same contacts
    or two different contacts from same device. Wire can contain only markers with equal wire names.
    """

    def __init__(self, frm: Marker, to: Marker, section: str):
        self.frm = frm
        self.to = to
        self._validate()
        self.section = section

    @property
    def name(self) -> str:
        self._validate()
        return self.frm.wire_name

    def _validate(self) -> None:
        is_different_wire_names = self.frm.wire_name != self.to.wire_name
        both_markers_have_supported_format = not self.frm.unsupported_format and not self.to.unsupported_format
        if is_different_wire_names and both_markers_have_supported_format:
            raise InvalidMarkersPairException

    def __str__(self) -> str:
        return f'{self.frm} -> {self.to}'

    def __repr__(self) -> str:
        return f'Wire(frm={repr(self.frm)}, to={repr(self.to)})'

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            raise NotImplemented
        return self.frm == other.frm and self.to == other.to

    @property
    def markers(self):
        return self.frm.label, self.to.label


class Device:
    def __init__(self, name: str):
        self.name = name
        self.wires: List[Wire] = []

    def add_wires(self, wires: List[Wire]) -> None:
        self.wires.extend(wires)

    @staticmethod
    def _get_sorting_priority(wire: Wire) -> Tuple[int, str, str, str]:
        if wire.frm.unsupported_format or wire.to.unsupported_format:
            lowest_priority = 0, '', '', ''
            return lowest_priority
        is_internal = 1 if wire.frm.device == wire.to.device else 0
        if wire.frm.jack:
            return is_internal, wire.frm.jack, wire.to.device, wire.frm.contact
        return is_internal, wire.to.device, wire.frm.wire_name, wire.frm.contact

    def sort(self):
        self.wires = sorted(self.wires, key=self._get_sorting_priority)
        return self

    @property
    def markers(self) -> List[Marker]:
        markers = []
        for wire in self.wires:
            markers.extend(wire.markers)
        return markers

    def __repr__(self) -> str:
        return f'Device(name={repr(self.name)}, wires={self.wires}'

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            raise NotImplemented
        return self.wires == other.wires and self.name == other.name


class Schematic:
    def __init__(self):
        self.content = {}

    def add_devices(self, devices: List[Device], section: str) -> None:
        """add devices with exact wire section"""
        self.content[section] = devices

    @property
    def all_devices(self) -> List[Device]:
        all_devices = []
        for section_devices in self.content.values():
            all_devices.extend(section_devices)
        return all_devices

    @property
    def all_wires(self) -> List[Wire]:
        all_wires = []
        for device in self.all_devices:
            all_wires.extend(device.wires)
        return all_wires

    def get_all_device_wires(self, name: str):
        device_wires = []
        for device in self.all_devices:
            if device.name == f'Device {name}':
                device_wires.extend(device.wires)
        return device_wires
