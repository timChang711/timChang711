# Simple 1-byte memory read/write utilities

# Simulated memory storage
_memory = {}


def write(addr: int, value: int) -> None:
    """Write a byte value to the given address."""
    if not 0 <= value <= 0xFF:
        raise ValueError("value must fit in one byte")
    _memory[addr & 0xFFFF] = value & 0xFF


def read(addr: int) -> int:
    """Read a byte from the given address. Returns 0 if not written."""
    return _memory.get(addr & 0xFFFF, 0)


def read_11bit_value(lsb_addr: int = 0x1A00, msb_addr: int = 0x1A01) -> int:
    """Read an 11-bit value stored across two addresses.

    The byte at ``lsb_addr`` contains the lower 8 bits. The lower three bits
    of the byte at ``msb_addr`` contain the most significant bits of the
    number.  All other bits in ``msb_addr`` are ignored.
    """
    lsb = read(lsb_addr)
    msb_bits = read(msb_addr) & 0x07  # only bits 0-2
    return (msb_bits << 8) | lsb


def set_bit0_at(addr: int = 0x1800) -> int:
    """Set bit 0 at the specified address and return the new byte value."""
    value = read(addr)
    value |= 0x01
    write(addr, value)
    return value


if __name__ == "__main__":
    # Example usage
    # Write sample values
    write(0x1A00, 0x5A)  # LSB
    write(0x1A01, 0x02)  # Only lower 3 bits used

    val_11bit = read_11bit_value()
    print(f"11-bit value: {val_11bit} (decimal)")

    write(0x1800, 0x00)
    new_val = set_bit0_at()
    print(f"0x1800 after setting bit0: 0x{new_val:02X}")
