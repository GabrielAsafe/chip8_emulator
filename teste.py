import random
import time
import sdl2.ext
import os
from Timers import Timers
from Keypad import Keypad
from Display import Chip8Display
from Memory import Memory
from Stack import Stack


class Chip8:
    def __init__(self):
        self.memory = Memory()  # Usando a classe Memory
        self.registers = [0] * 16  # Registradores V0-VF
        self.index_register = 0  # Registrador de índice
        self.pc = 0x200  # Contador de programa (inicia em 0x200)
        self.stack = Stack()  # Pilha de sub-rotinas
        self.display = Chip8Display()  # Classe de exibição
        self.timers = Timers()  # Classe de timers
        self.keypad = Keypad()  # Classe de controle do teclado
        self.running = True  # Indicador de execução
        self.waiting_for_key = False  # Controle para espera de tecla
        self.display = Chip8Display(scale=10)

    def fetch_opcode(self):
        """Busca o próximo opcode (16 bits) da memória."""
        high_byte = self.memory.read_byte(self.pc)  # Agora funciona com __getitem__
        low_byte = self.memory.read_byte(self.pc + 1)  # Acessa corretamente
        opcode = (high_byte << 8) | low_byte
        self.pc += 2  # Incrementa o contador de programa
        return opcode

    def decode_execute(self, opcode):
        """Decodifica e executa a instrução."""
        first_nibble = (opcode & 0xF000) >> 12
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        n = opcode & 0x000F
        nn = opcode & 0x00FF
        nnn = opcode & 0x0FFF

        if opcode == 0x00E0:  # CLS - Limpa a tela
            self.display.clear()
        elif opcode == 0x00FF:  # Hires - Muda para gráficos de alta resolução
            self.display.set_high_resolution(True)
        elif opcode == 0x00FE:  # LoRes - Muda para gráficos de baixa resolução
            self.display.set_high_resolution(False)
        elif (opcode & 0xF000) == 0xD000:  # DRW VX, VY, N - Desenha um sprite
            self.display.draw_sprite(self.registers[x], self.registers[y], self.memory.read_memory(self.index_register, n))
        elif opcode == 0x00FB:  # Scroll Right
            self.display.scroll_right()
        elif opcode == 0x00FC:  # Scroll Left
            self.display.scroll_left()
        elif (opcode & 0x00F0) == 0x00C0:  # Scroll Down
            self.display.scroll_down(n)
        elif (opcode & 0xF000) == 0x8000:  # Shifts: 8XY6 e 8XYE
            if n == 0x6:  # 8XY6: VX := VX shr 1, VF := carry
                self.registers[x] >>= 1
                self.registers[0xF] = self.registers[x] & 0x01  # VF = carry
            elif n == 0xE:  # 8XYE: VX := VX shl 1, VF := carry
                self.registers[x] <<= 1
                self.registers[0xF] = (self.registers[x] >> 7) & 0x01  # VF = carry
        elif (opcode & 0xF000) == 0x2000:  # 2NNN - Chama sub-rotina
            self.stack.push(self.pc)
            self.pc = nnn
        elif (opcode & 0xF000) == 0x4000:  # 4XNN - Se VX != NN
            if self.registers[x] != nn:
                self.pc += 2
        elif (opcode & 0xF000) == 0x6000:  # 6XNN - Se VX = NN
            self.registers[x] = nn
        elif (opcode & 0xF000) == 0x7000:  # 7XNN - Adiciona NN a VX
            self.registers[x] += nn
        elif (opcode & 0xF000) == 0x8000:  # 8XY0 - VX = VY
            self.registers[x] = self.registers[y]
        elif (opcode & 0xF000) == 0x8001:  # 8XY1 - VX = VX | VY
            self.registers[x] |= self.registers[y]
        elif (opcode & 0xF000) == 0x8002:  # 8XY2 - VX = VX & VY
            self.registers[x] &= self.registers[y]
        elif (opcode & 0xF000) == 0x8003:  # 8XY3 - VX = VX ^ VY
            self.registers[x] ^= self.registers[y]
        elif (opcode & 0xF000) == 0x8004:  # 8XY4 - VX = VX + VY (com carry)
            result = self.registers[x] + self.registers[y]
            self.registers[0xF] = 1 if result > 255 else 0  # VF = carry
            self.registers[x] = result & 0xFF
        elif (opcode & 0xF000) == 0x8005:  # 8XY5 - VX = VX - VY
            self.registers[0xF] = 1 if self.registers[x] > self.registers[y] else 0  # VF = borrow
            self.registers[x] = (self.registers[x] - self.registers[y]) & 0xFF
        elif (opcode & 0xF000) == 0x8006:  # 8XY6 - VX = VX >> 1
            self.registers[0xF] = self.registers[x] & 0x01  # VF = LSB before shift
            self.registers[x] >>= 1
        elif (opcode & 0xF000) == 0x8007:  # 8XY7 - VX = VY - VX
            self.registers[0xF] = 1 if self.registers[y] > self.registers[x] else 0  # VF = borrow
            self.registers[x] = (self.registers[y] - self.registers[x]) & 0xFF
        elif (opcode & 0xF000) == 0x800E:  # 8XYE - VX = VX << 1
            self.registers[0xF] = (self.registers[x] >> 7) & 0x01  # VF = MSB before shift
            self.registers[x] <<= 1
        elif (opcode & 0xF000) == 0xA000:  # ANNN - I = NNN
            self.index_register = nnn
        elif (opcode & 0xF000) == 0xB000:  # BNNN - PC = NNN + V0
            self.pc = nnn + self.registers[0]
        elif (opcode & 0xF000) == 0xC000:  # CXNN - VX = random() & NN
            self.registers[x] = random.randint(0, 255) & nn
        elif (opcode & 0xF000) == 0xD000:  # DRW VX, VY, N - Desenha um sprite
            self.display.draw_sprite(self.registers[x], self.registers[y], self.memory.read_memory(self.index_register, n))
        elif (opcode & 0xF000) == 0xE000:  # ExXX - Checagem de tecla pressionada
            if nn == 0x9E:  # EX9E - Se a tecla VX for pressionada
                if self.keypad.is_pressed(self.registers[x]):
                    self.pc += 2
            elif nn == 0xA1:  # EXA1 - Se a tecla VX não for pressionada
                if not self.keypad.is_pressed(self.registers[x]):
                    self.pc += 2
        elif (opcode & 0xF000) == 0xF000:
            if nn == 0x07:  # FX07 - VX = Delay Timer
                self.registers[x] = self.timers.get_delay()
            elif nn == 0x15:  # FX15 - Delay Timer = VX
                self.timers.set_delay(self.registers[x])
            elif nn == 0x18:  # FX18 - Sound Timer = VX
                self.timers.set_sound(self.registers[x])
            elif nn == 0x1E:  # FX1E - I = I + VX
                self.index_register += self.registers[x]
            elif nn == 0x29:  # FX29 - I = Sprite for VX
                self.index_register = self.registers[x] * 5
            elif nn == 0x33:  # FX33 - BCD for VX
                self.memory.write_byte(self.index_register, self.registers[x] // 100)
                self.memory.write_byte(self.index_register + 1, (self.registers[x] // 10) % 10)
                self.memory.write_byte(self.index_register + 2, self.registers[x] % 10)
            elif nn == 0x55:  # FX55 - Armazena V0..VX na memória
                for i in range(x + 1):
                    self.memory.write_byte(self.index_register + i, self.registers[i])
                self.index_register += x + 1
            elif nn == 0x65:  # FX65 - Lê V0..VX da memória
                for i in range(x + 1):
                    self.registers[i] = self.memory.read_byte(self.index_register + i)
                self.index_register += x + 1
        else:
            print(f"Opcode não implementado: {hex(opcode)}")

    def run(self):
        while self.running:
            opcode = self.fetch_opcode()  # Busca o próximo opcode
            self.decode_execute(opcode)  # Decodifica e executa a instrução
            self.display.render()  # Atualiza a tela
            self.handle_events()  # Lida com eventos (ex: janela fechando)
            time.sleep(1/700)  # Aproximadamente 700 instruções por segundo

    def handle_events(self):
        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_QUIT:
                self.running = False

    def dump_memory(self, start=0, end=0xFFF, bytes_per_row=16):
        """
        Exibe um dump da memória, do endereço `start` ao `end`.
        Cada linha mostrará `bytes_per_row` bytes em formato hexadecimal.
        
        Args:
            start: Endereço inicial para o dump (padrão é 0).
            end: Endereço final para o dump (padrão é 0xFFF, o fim da memória).
            bytes_per_row: Quantidade de bytes por linha.
        """
        for i in range(start, end, bytes_per_row):
            # Imprime o endereço de memória e os bytes correspondentes
            line = f"{i:03X}: "
            line += " ".join(f"{self.memory.read_byte(j):02X}" for j in range(i, min(i + bytes_per_row, end + 1)))
            print(line)

# Testando o emulador com timers
if __name__ == "__main__":
    chip8 = Chip8()
    rom_path = os.path.abspath('res/rom/BC_test.ch8')

    # Lê a ROM e carrega na memória do CHIP-8
    with open(rom_path, "rb") as rom_file:
        rom_data = rom_file.read()  # Lê todo o conteúdo da ROM
        
    # Carregar a ROM na memória a partir do endereço 0x200
    for i in range(len(rom_data)):
        chip8.memory.write_byte(0x200 + i, rom_data[i])  # Usando __setitem__
 
    chip8.run()
