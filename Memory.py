import os

class Memory:
    def __init__(self):
        self.memory = bytearray(4096)  # 4 KB de memória
        self.load_fontset()  # Carrega as fontes

    def load_fontset(self):
        """Carrega os caracteres da fonte na memória, a partir do endereço 0x50."""
        fontset = [
            0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
            0x20, 0x60, 0x20, 0x20, 0x70,  # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
            0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
            0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
            0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
            0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
            0xF0, 0x80, 0xF0, 0x80, 0x80   # F
        ]
        self.memory[0x50:0x50 + len(fontset)] = fontset

    def __getitem__(self, idx):
        if idx < 0 or idx >= len(self.memory):
            raise IndexError("Índice fora dos limites da memória")
        return self.memory[idx]

    def __setitem__(self, idx, value):
        if idx < 0 or idx >= len(self.memory):
            raise IndexError("Índice fora dos limites da memória")
        self.memory[idx] = value

    def read_byte(self, address):
        """Lê um byte da memória."""
        return self.memory[address]

    def write_byte(self, address, value):
        """Escreve um byte na memória."""
        self.memory[address] = value

    def load_rom(self, rom_data, start_address=0x200):
        """Carrega um programa na memória a partir do endereço 0x200."""
        rom_size = len(rom_data)
        if start_address + rom_size > 4096:
            raise ValueError("ROM muito grande para a memória disponível")
        self.memory[start_address:start_address + rom_size] = rom_data

    def read_memory(self, index, size):
        """Lê `size` bytes a partir do índice `index`."""
        return self.memory[index:index + size]

    def dump_memory(self, start=0, end=0xFFF, bytes_per_row=16):
        """Exibe um dump da memória do endereço `start` ao `end`."""
        for i in range(start, end, bytes_per_row):
            line = f"{i:03X}: "
            line += " ".join(f"{self.memory[j]:02X}" for j in range(i, min(i + bytes_per_row, end + 1)))
            print(line)

    def select_rom(self, path):
        """Lê um arquivo ROM e carrega na memória do CHIP-8."""
        rom_path = os.path.abspath(path)
        
        if not os.path.exists(rom_path):
            raise FileNotFoundError(f"Arquivo ROM não encontrado: {rom_path}")

        with open(rom_path, "rb") as rom_file:
            rom_data = rom_file.read()
        
        self.load_rom(rom_data)

if __name__ == '__main__':
    chip8 = Memory()
    chip8.select_rom('res/rom/BC_test.ch8')
    chip8.dump_memory(0x0, 0x1000)
