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
        self.stack = []  # Pilha de sub-rotinas
        self.display = Chip8Display()  # Classe de exibição
        self.timers = Timers()  # Classe de timers
        self.running = True  # Indicador de execução
        self.waiting_for_key = False  # Controle para espera de tecla
        self.display = Chip8Display(scale=10)


    def fetch_opcode(self):
        """Busca o próximo opcode (16 bits) da memória."""
        high_byte = self.memory[self.pc]  # Agora funciona com __getitem__
        low_byte = self.memory[self.pc + 1]  # Acessa corretamente
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
            self.display.draw_sprite(self.registers[x], self.registers[y], self.memory.memory[self.index_register:self.index_register + n])
        elif opcode == 0x00FB:  # Scroll Right
            self.display.scroll_right()
        elif opcode == 0x00FC:  # Scroll Left
            self.display.scroll_left()
        elif (opcode & 0x00F0) == 0x00C0:  # Scroll Down
            n = opcode & 0x000F
            self.display.scroll_down(n)
        elif (opcode & 0xF000) == 0x8000:  # Shifts: 8XY6 e 8XYE
            if n == 0x6:  # 8XY6: VX := VX shr 1, VF := carry
                self.registers[x] >>= 1
                self.registers[0xF] = self.registers[x] & 0x01  # VF = carry
            elif n == 0xE:  # 8XYE: VX := VX shl 1, VF := carry
                self.registers[x] <<= 1
                self.registers[0xF] = (self.registers[x] >> 7) & 0x01  # VF = carry
            elif opcode == 0xF055:  # FX55: Salva V0..VX na memória a partir de I
                for i in range(x + 1):
                    self.memory.write_byte(self.index_register + i, self.registers[i])
                self.index_register += x + 1
            elif opcode == 0xF065:  # FX65: Lê V0..VX da memória a partir de I
                for i in range(x + 1):
                    self.registers[i] = self.memory.read_byte(self.index_register + i)
                self.index_register += x + 1

        elif opcode == 0x00FD:  # FX Exit - Sai do programa
            self.running = False
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
            line += " ".join(f"{self.memory[j]:02X}" for j in range(i, min(i + bytes_per_row, end + 1)))
            print(line)

# Testando o emulador com timers
if __name__ == "__main__":
    chip8 = Chip8()
    # Caminho para a ROM .ch8
    rom_path = os.path.abspath('res/rom/BC_test.ch8')

    # Lê a ROM e carrega na memória do CHIP-8
    with open(rom_path, "rb") as rom_file:
        rom_data = rom_file.read()  # Lê todo o conteúdo da ROM
        
    # Carregar a ROM na memória a partir do endereço 0x200
    for i in range(len(rom_data)):
        chip8.memory[0x200 + i] = rom_data[i]  # Usando __setitem__
 
    #chip8.dump_memory(0x200, 0x1000)
    
    
    chip8.run()
