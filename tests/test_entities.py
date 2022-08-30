from copy import deepcopy
from pprint import pprint

import pytest
from contextlib import nullcontext as does_not_raise

from entities import Marker, Wire, Device, Schematic
from exceptions import UnsupportedMarkerFormatException, InvalidMarkersPairException
from utils import flatten_list


@pytest.fixture
def valid_label_example():
    return 'A1:X4-1 952'


@pytest.fixture
def marker_with_valid_label_example(valid_label_example):
    return Marker(label=valid_label_example)


@pytest.fixture
def wire_markers_pair():
    return Marker(label='A1:X4-1 952').parse(), Marker(label='X3:15:2 952').parse()


@pytest.fixture
def valid_wire(wire_markers_pair):
    return Wire(frm=wire_markers_pair[0], to=wire_markers_pair[1], section='1.0')


@pytest.fixture
def device_without_wires():
    return Device(name='Device A1')


@pytest.fixture
def list_of_10_wires():
    return [
        Wire(frm=Marker('A1:X6-12 959').parse(), to=Marker('X8:34:1 959').parse(), section='1,0'),
        Wire(frm=Marker('A1:X3-2 1701').parse(), to=Marker('A1:X3-6 1701').parse(), section='1,0'),
        Wire(frm=Marker('A1:X6-11 960').parse(), to=Marker('X8:36:1 960').parse(), section='1,0'),
        Wire(frm=Marker('A1:GND2').parse(), to=Marker('A1:X1.1.1-1').parse(), section='1,0'),
        Wire(frm=Marker('A1:X3-8 881').parse(), to=Marker('SAC3:4.3 881').parse(), section='1,0'),
        Wire(frm=Marker('SF2:3 +EC').parse(), to=Marker('SF4:3 +EC').parse(), section='1,0'),
        Wire(frm=Marker('XS1:16 43-TH1').parse(), to=Marker('X4:26:1 43-TH1').parse(), section='1,0'),
        Wire(frm=Marker('SQP1:21 81').parse(), to=Marker('X2:62:2 81').parse(), section='1,0'),
        Wire(frm=Marker('TAB1:4И1 N411').parse(), to=Marker('X1:39:1 N411').parse(), section='1,0'),
        Wire(frm=Marker('SFB1:1 -EC').parse(), to=Marker('SFT1:1 -EC').parse(), section='1,0'),
    ]


@pytest.fixture
def device_a1(list_of_10_wires):
    wires = list_of_10_wires[:5]
    device = Device('Device A1')
    device.add_wires(wires)
    return device


@pytest.fixture
def empty_schematic():
    return Schematic()


@pytest.fixture
def schematic_with_content(empty_schematic, expected_sorted_schematic):
    empty_schematic.content = deepcopy(expected_sorted_schematic)
    return empty_schematic


@pytest.fixture
def expected_all_devices(schematic_with_content):
    return flatten_list(schematic_with_content.content.values())


@pytest.fixture
def expected_all_wires(expected_all_devices):
    return flatten_list([device.wires for device in expected_all_devices])


class TestMarker:
    def test_creation(self, valid_label_example):
        marker = Marker(label=valid_label_example)
        assert marker.label == valid_label_example
        assert marker.wire_name is None
        assert marker.device is None
        assert marker.jack is None
        assert marker.contact is None
        assert marker.connection is None

    @pytest.mark.parametrize(
        'label,wire_name,device,jack,contact,connection',
        [
            pytest.param(
                'X2:14:1 9', '9', 'X2', None, '14', '1', id='with connection'
            ),
            pytest.param(
                'A1:X4-1 952', '952', 'A1', 'X4', '1', None, id='with jack'
            ),
            pytest.param(
                'A1:GND2', None, 'A1', None, 'GND2', None, id='only device and contact'
            ),
            pytest.param(
                'PE:PE', None, 'PE', None, 'PE', None, id='only device and contact'
            ),
            pytest.param(
                'SF1:2 2', '2', 'SF1', None, '2', None, id='without jack and connection'
            )
        ]
    )
    def test_parse(self, label: str, wire_name, device, jack, contact, connection):
        marker = Marker(label=label)
        marker.parse()
        marker_attrs_values = marker.label, marker.wire_name, marker.device, marker.jack, marker.contact, marker.connection
        expected = label, wire_name, device, jack, contact, connection

        assert marker_attrs_values == expected

    @pytest.mark.parametrize(
        'label',
        [
            '',
            'Device A1',
            'A1 X4-5:1 46',
            'SF1:11  ',
            'SG:- 1A1',
        ]
    )
    def test_parse_unsupported_formats(self, label):
        marker = Marker(label=label)
        with pytest.raises(UnsupportedMarkerFormatException):
            marker.parse()

    @pytest.mark.parametrize(
        'label,expected_address',
        [
            pytest.param('X2:14:1 9', 'X2:14:1'),
            pytest.param('A1:X4-1 952', 'A1:X4-1'),
            pytest.param('A1:GND2', 'A1:GND2'),
            pytest.param('SF1:2 2', 'SF1:2'),
        ]
    )
    def test_address_property(self, label: str, expected_address):
        marker = Marker(label=label)
        marker.parse()
        assert marker.address == expected_address

    def test_dander_repr(self, marker_with_valid_label_example, valid_label_example):
        marker_repr = repr(valid_label_example)
        assert repr(marker_with_valid_label_example) == f'Marker(label={marker_repr})'

    @pytest.mark.parametrize(
        'marker_obj,expected_string',
        [
            pytest.param(Marker(label='X2:14:1 9'), 'X2:14:1 9'),
            pytest.param(Marker(label='A1:X4-1 952'), 'A1:X4-1 952'),
            pytest.param(Marker(label='A1:GND2'), 'A1:GND2'),
            pytest.param(Marker(label='SF1:2 2'), 'SF1:2 2'),
        ]
    )
    def test_dander_str(self, marker_obj: Marker, expected_string: str):
        marker_obj.parse()
        assert str(marker_obj) == expected_string

    def test_dander_eq(self):
        marker1 = Marker('A1:X6-12 959').parse()
        marker2 = Marker('A1:X6-12 959').parse()
        marker3 = Marker('A1:X5-1 99').parse()

        assert marker1 == marker2
        assert marker1 != marker3
        assert [marker1, marker2] == [marker1, marker2]
        assert [marker1, marker3] != [marker3, marker1]
        assert [marker1, marker2] != [marker1, marker2, marker3]


class TestWire:
    @pytest.mark.parametrize(
        'first,second,expected_name,expectation',
        [
            pytest.param(
                'X2:14:1 952', 'X3:15:2 952', '952', does_not_raise()
            ),
            pytest.param(
                'PE:PE', 'XPE5:1', None, does_not_raise()
            ),
            pytest.param(
                'X4:14:1 1', 'X3:5:1 2', None, pytest.raises(InvalidMarkersPairException)
            ),
        ]
    )
    def test_creation(self, first: str, second: str, expected_name, expectation):
        first_marker = Marker(label=first).parse()
        second_marker = Marker(label=second).parse()
        with expectation:
            wire = Wire(frm=first_marker, to=second_marker, section='1,0')
            assert wire.name == expected_name
            assert (wire.frm, wire.to) == (first_marker, second_marker)

    def test_dander_str(self, valid_wire, wire_markers_pair):
        assert str(valid_wire) == f'{wire_markers_pair[0]} -> {wire_markers_pair[1]}'

    def test_dander_repr(self, valid_wire, wire_markers_pair):
        assert repr(valid_wire) == f'Wire(frm={repr(wire_markers_pair[0])}, to={repr(wire_markers_pair[1])})'


class TestDevice:
    def test_creation(self):
        device_name = 'Device A1'
        device = Device(name=device_name)
        assert device.name == device_name
        assert isinstance(device.wires, list)
        assert len(device.wires) == 0

    def test_add_wires(self, device_without_wires, valid_wire):
        assert len(device_without_wires.wires) == 0
        device_without_wires.add_wires([valid_wire])
        assert len(device_without_wires.wires) == 1
        device_without_wires.add_wires([valid_wire, valid_wire, valid_wire])
        assert len(device_without_wires.wires) == 4

    @pytest.mark.parametrize(
        'wire,expected_priority',
        [
            pytest.param(Wire(frm=Marker('A1:X5-1 2').parse(), to=Marker('A1:X5-3 2').parse(), section='1,0'),
                         (1, 'X5', 'A1', '1')),
            pytest.param(Wire(frm=Marker('A1:X5-2 29').parse(), to=Marker('X5:18:1 29').parse(), section='1,0'),
                         (0, 'X5', 'X5', '2')),
            pytest.param(
                Wire(frm=Marker('SAC3:2.3 1').parse(), to=Marker('SAC3:1.1 1').parse(), section='1,0'),
                (1, 'SAC3', '1', '2.3')
            ),
            pytest.param(
                Wire(frm=Marker('ADR1:2 D13').parse(), to=Marker('X0:20:1 D13').parse(), section='1,0'),
                (0, 'X0', 'D13', '2')
            ),
        ]
    )
    def test__get_sorting_priority(self, wire, expected_priority):
        priority = Device._get_sorting_priority(wire)
        assert priority == expected_priority

    def test_markers_property(self, device_a1):
        expected_markers = [
            'A1:X6-12 959', 'X8:34:1 959',
            'A1:X3-2 1701', 'A1:X3-6 1701',
            'A1:X6-11 960', 'X8:36:1 960',
            'A1:GND2', 'A1:X1.1.1-1',
            'A1:X3-8 881', 'SAC3:4.3 881',
        ]

        assert device_a1.markers == expected_markers

    def test_dander_repr(self, device_a1):
        assert repr(device_a1) == f'Device(name={repr(device_a1.name)}, wires={device_a1.wires}'


class TestSchematic:
    def test_add_devices(self, empty_schematic, expected_sorted_schematic):
        wire_section = '1,0'
        devices = expected_sorted_schematic[wire_section]
        empty_schematic.add_devices(devices=devices, section=wire_section)
        assert empty_schematic.content[wire_section] == devices

    def test_all_devices_property(self, schematic_with_content, expected_all_devices):
        assert schematic_with_content.all_devices == expected_all_devices

    def test_all_wires_property(self, schematic_with_content, expected_all_wires):
        assert schematic_with_content.all_wires == expected_all_wires

    def test_get_all_device_wires(self, schematic_with_content):
        all_wires = schematic_with_content.get_all_device_wires('U1')

        assert len(all_wires) == 19

        for wire in all_wires:
            assert wire.frm.device == 'U1'
