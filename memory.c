#include <stdio.h>
#include <stdint.h>
#include <string.h>

#define MEM_SIZE 65536
static uint8_t memory[MEM_SIZE];

void write_byte(uint16_t addr, uint8_t value) {
    memory[addr & 0xFFFF] = value;
}

uint8_t read_byte(uint16_t addr) {
    return memory[addr & 0xFFFF];
}

unsigned int read_11bit_value(uint16_t lsb_addr, uint16_t msb_addr) {
    uint8_t lsb = read_byte(lsb_addr);
    uint8_t msb_bits = read_byte(msb_addr) & 0x07;
    return (msb_bits << 8) | lsb;
}

uint8_t set_bit0_at(uint16_t addr) {
    uint8_t value = read_byte(addr);
    value |= 0x01;
    write_byte(addr, value);
    return value;
}

int main(void) {
    // Example usage
    memset(memory, 0, sizeof(memory));
    write_byte(0x1A00, 0x5A);
    write_byte(0x1A01, 0x02);

    unsigned int val_11bit = read_11bit_value(0x1A00, 0x1A01);
    printf("11-bit value: %u (decimal)\n", val_11bit);

    write_byte(0x1800, 0x00);
    uint8_t new_val = set_bit0_at(0x1800);
    printf("0x1800 after setting bit0: 0x%02X\n", new_val);

    return 0;
}
