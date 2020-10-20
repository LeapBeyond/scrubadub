from .base import Filth


class AddressFilth(Filth):
    type = 'address'


class GBAddressFilth(AddressFilth):
    type = 'gb_address'


class USAddressFilth(AddressFilth):
    type = 'us_address'
