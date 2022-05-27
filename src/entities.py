from exceptions import UnsupportedMarkerFormatException


class Marker:
    # FIXME: make loading this constants from settings
    WIRE_SEP = ' '
    ADDRESS_SEP = ':'
    JACK_SEP = '-'

    def __init__(self, label: str):
        self.label = label
        self.wire_name = None
        self.device = None
        self.jack = None
        self.contact = None
        self.connection = None

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
            raise UnsupportedMarkerFormatException

        if self.label.count(self.ADDRESS_SEP) == 1:
            self.device, self.contact = address.split(self.ADDRESS_SEP)
        elif self.label.count(self.ADDRESS_SEP) == 2:
            self.device, self.contact, self.connection = address.split(self.ADDRESS_SEP)
        else:
            raise UnsupportedMarkerFormatException

        if self.contact.count(self.JACK_SEP) == 1:
            self.jack, self.contact = self.contact.split(self.JACK_SEP)
            # check that self.jack and self.contact contains useful information
            assert self.jack
            assert self.contact
        return self

    @property
    def address(self):
        if self.jack:
            address_params = [self.device, self.jack, self.contact]
        else:
            address_params = [self.device, self.contact]

        if self.connection:
            address_params.append(self.connection)

        return self.ADDRESS_SEP.join(address_params)

    def __repr__(self):
        marker_repr = repr(self.label)
        return f'Marker(label={marker_repr})'

    def __str__(self):
        marker_data = [self.address]
        if self.wire_name:
            marker_data.append(self.wire_name)
        return self.WIRE_SEP.join(marker_data)


class Wire:
    def __init__(self, frm: Marker, to: Marker):
        self.frm = frm
        self.to = to

    @property
    def name(self):
        assert self.frm.wire_name == self.to.wire_name
        return self.frm.wire_name

    def __str__(self):
        return f'{self.frm} -> {self.to}'

    def __repr__(self):
        return f'Wire(frm={repr(self.frm)}, to={repr(self.to)})'


class Device:
    def __init__(self, name: str):
        self.name = name
        self.wires = []

    def add_wires(self, wires: list[Wire]):
        self.wires.extend(wires)

    @staticmethod
    def get_sorting_priority(wire: Wire) -> tuple:
        is_internal = 1 if wire.frm.device == wire.to.device else 0
        if wire.frm.jack:
            return is_internal, wire.frm.jack, wire.to.device, wire.frm.contact
        return is_internal, wire.frm.contact, wire.to.device

    def sort(self):
        self.wires = sorted(self.wires, key=self.get_sorting_priority)
        return self

    def markers(self):
        markers = []
        for wire in self.wires:
            markers.extend([wire.frm, wire.to])
        return markers

    def __repr__(self):
        return f'Device(name={repr(self.name)}, wires={self.wires}'
