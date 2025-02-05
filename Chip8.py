import time
import sdl2.ext
import random
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
        self.stack = Stack()
        self.display = Chip8Display()  # Classe de exibição
        self.timers = Timers()  # Classe de timers
        self.running = True  # Indicador de execução
        self.waiting_for_key = False  # Controle para espera de tecla
        self.display = Chip8Display(scale=10)


    def fetch_opcode(self):
        """Busca o próximo opcode (16 bits) da memória."""
        high_byte = self.memory[self.pc]  # primeiro byte(olhando o hex do programa de teste)
        low_byte = self.memory[self.pc + 1]  # segundo byte
        opcode = (high_byte << 8) | low_byte #TODO não devia ser 16 ?? 
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
        elif opcode == 0x00EE:  # RET - Retorna da subrotina
            self.pc = self.stack.pop()
        elif first_nibble == 0x1:  # JP addr - Pula para NNN
            self.pc = nnn
        elif first_nibble == 0x2:  # CALL addr - Chama subrotina
            self.stack.append(self.pc)
            self.pc = nnn
        elif first_nibble == 0x3:  # SE Vx, NN - Pula se VX == NN
            if self.registers[x] == nn:
                self.pc += 2
        elif first_nibble == 0x4:  # SNE Vx, NN - Pula se VX != NN
            if self.registers[x] != nn:
                self.pc += 2
        elif first_nibble == 0x5 and n == 0:  # SE Vx, Vy - Pula se VX == VY
            if self.registers[x] == self.registers[y]:
                self.pc += 2
        elif first_nibble == 0x6:  # LD Vx, NN - Atribui NN para VX
            self.registers[x] = nn
        elif first_nibble == 0x7:  # ADD Vx, NN - Soma NN a VX
            self.registers[x] = (self.registers[x] + nn) & 0xFF
        elif first_nibble == 0x8:
            if n == 0x0:  # LD Vx, Vy - VX := VY
                self.registers[x] = self.registers[y]
            elif n == 0x1:  # OR Vx, Vy - VX := VX OR VY
                self.registers[x] |= self.registers[y]
            elif n == 0x2:  # AND Vx, Vy - VX := VX AND VY
                self.registers[x] &= self.registers[y]
            elif n == 0x3:  # XOR Vx, Vy - VX := VX XOR VY
                self.registers[x] ^= self.registers[y]
            elif n == 0x4:  # ADD Vx, Vy - VX := VX + VY, VF := Carry
                sum_val = self.registers[x] + self.registers[y]
                self.registers[0xF] = 1 if sum_val > 255 else 0
                self.registers[x] = sum_val & 0xFF
            elif n == 0x5:  # SUB Vx, Vy - VX := VX - VY, VF := Not Borrow
                self.registers[0xF] = 1 if self.registers[x] > self.registers[y] else 0
                self.registers[x] = (self.registers[x] - self.registers[y]) & 0xFF
            elif n == 0x6:  # SHR Vx - VX := VX >> 1, VF := Bit Menos Significativo
                self.registers[0xF] = self.registers[x] & 0x1
                self.registers[x] >>= 1
            elif n == 0x7:  # SUBN Vx, Vy - VX := VY - VX, VF := Not Borrow
                self.registers[0xF] = 1 if self.registers[y] > self.registers[x] else 0
                self.registers[x] = (self.registers[y] - self.registers[x]) & 0xFF
            elif n == 0xE:  # SHL Vx - VX := VX << 1, VF := Bit Mais Significativo
                self.registers[0xF] = (self.registers[x] >> 7) & 0x1
                self.registers[x] = (self.registers[x] << 1) & 0xFF
        elif first_nibble == 0x9 and n == 0x0:  # SNE Vx, Vy - Pula se VX != VY
            if self.registers[x] != self.registers[y]:
                self.pc += 2
        elif first_nibble == 0x1:  # JP addr - Pula para NNN
            self.pc = nnn

        elif first_nibble == 0x6:  # LD Vx, NN - Atribui NN para VX
            self.registers[x] = nn

        elif first_nibble == 0x7:  # ADD Vx, NN - Soma NN a VX
            self.registers[x] = (self.registers[x] + nn) & 0xFF  # Garante overflow de 8 bits

        elif first_nibble == 0xA:  # LD I, addr - I := NNN
            self.index_register = nnn

        elif first_nibble == 0xD:  # DRW Vx, Vy, N - Desenha sprite
            sprite = self.memory.read_memory(self.index_register, n)
            collision = self.display.draw_sprite(self.registers[x], self.registers[y], sprite)
            self.registers[0xF] = 1 if collision else 0  # VF = 1 se houve colisão, senão 0


        elif first_nibble == 0xA:  # LD I, addr - I := NNN
            self.index_register = nnn
        elif first_nibble == 0xB:  # JP V0, addr - PC := NNN + V0
            self.pc = nnn + self.registers[0]
        elif first_nibble == 0xC:  # RND Vx, NN - VX := Rand() & NN
            self.registers[x] = random.randint(0, 255) & nn
        elif first_nibble == 0xD:  # DRW Vx, Vy, N - Desenha sprite
            self.display.draw_sprite(self.registers[x], self.registers[y], self.memory.memory[self.index_register:self.index_register + n])
        elif first_nibble == 0xF:
            if nn == 0x07:  # FX07 - VX := Delay Timer
                self.registers[x] = self.delay_timer
            elif nn == 0x15:  # FX15 - Delay Timer := VX
                self.delay_timer = self.registers[x]
            elif nn == 0x1E:  # FX1E - I := I + VX
                self.index_register += self.registers[x]
            elif nn == 0x29:  # FX29 - I := Localização do dígito de VX
                self.index_register = self.registers[x] * 5
            elif nn == 0x55:  # FX55 - Armazena V0..VX na memória a partir de I
                for i in range(x + 1):
                    self.memory.write_byte(self.index_register + i, self.registers[i])
            elif nn == 0x65:  # FX65 - Lê V0..VX da memória a partir de I
                for i in range(x + 1):
                    self.registers[i] = self.memory.read_byte(self.index_register + i)
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
                

# Testando o emulador com timers
if __name__ == "__main__":
    chip8 = Chip8()

    chip8.memory.select_rom('res/rom/BC_test.ch8')

    chip8.memory.dump_memory(0x200, 0x1000)
    
    chip8.run()
