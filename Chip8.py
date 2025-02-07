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
        self.display = Chip8Display(scale=15)
        self.keypad = Keypad()


    def fetch_opcode(self):
        """Busca o próximo opcode (16 bits) da memória."""
        high_byte = self.memory[self.pc]  # primeiro byte(olhando o hex do programa de teste)
        low_byte = self.memory[self.pc + 1]  # segundo byte
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

        ####print(f"Decodificando opcode: {hex(opcode)}")
        ####print(f"first_nibble: {first_nibble}, x: {x}, y: {y}, n: {n}, nn: {nn}, nnn: {nnn}")
        
        if opcode == 0x00E0:  # CLS - Limpa a tela
            ####print("Executando CLS - Limpa a tela")
            self.display.clear()
        elif opcode == 0x00EE:  # RET - Retorna da subrotina
            ####print("Executando RET - Retorna da subrotina")
            self.pc = self.stack.pop()
        elif first_nibble == 0x1:  # JP addr - Pula para NNN
            if self.pc == nnn:
                ####print(f"Evitar salto para o mesmo endereço {hex(self.pc)}")
                return  # Não fazer nada se o endereço de salto for o mesmo
            ####print(f"Executando JP addr - Pula para {hex(nnn)}")
            self.pc = nnn  # Atualiza o ponteiro do programa para o endereço nnn


        elif nn == 0x33:  # FX33 - Armazena a representação BCD de VX em memória[I, I+1, I+2]
            ####print(f"Executando FX33 - Convertendo VX ({self.registers[x]}) para BCD e armazenando na memória")
            valor = self.registers[x]
            self.memory.write_byte(self.index_register, valor // 100)       # Centena
            self.memory.write_byte(self.index_register + 1, (valor // 10) % 10)  # Dezena
            self.memory.write_byte(self.index_register + 2, valor % 10)     # Unidade


        elif first_nibble == 0x2:  # CALL addr - Chama subrotina
            ####print(f"Executando CALL addr - Chama subrotina para {hex(nnn)}")
            self.stack.push(self.pc)
            self.pc = nnn
        elif first_nibble == 0x3:  # SE Vx, NN - Pula se VX == NN
            ####print(f"Executando SE Vx, NN - Comparando VX ({self.registers[x]}) com NN ({nn})")
            if self.registers[x] == nn:
                self.pc += 2
        elif first_nibble == 0x4:  # SNE Vx, NN - Pula se VX != NN
            ####print(f"Executando SNE Vx, NN - Comparando VX ({self.registers[x]}) com NN ({nn})")
            if self.registers[x] != nn:
                self.pc += 2
            
        elif first_nibble == 0x5 and n == 0x0:  # SE Vx, Vy - Pula se VX == VY
            ####print(f"Executando SE Vx, Vy - Comparando VX ({self.registers[x]}) com VY ({self.registers[y]})")
            if self.registers[x] == self.registers[y]:
                self.pc += 2  # Avança apenas se os valores forem iguais


        elif first_nibble == 0x6:  # LD Vx, NN - Atribui NN para VX
            ####print(f"Executando LD Vx, NN - Atribuindo {nn} para VX")
            self.registers[x] = nn
        elif first_nibble == 0x7:  # ADD Vx, NN - Soma NN a VX
            ####print(f"Executando ADD Vx, NN - Somando {nn} a VX ({self.registers[x]})")
            self.registers[x] = (self.registers[x] + nn) & 0xFF
        elif first_nibble == 0x8:
            if n == 0x0:  # LD Vx, Vy - VX := VY
                ####print(f"Executando LD Vx, Vy - Atribuindo VX ({self.registers[x]}) a VY ({self.registers[y]})")
                self.registers[x] = self.registers[y]
            elif n == 0x1:  # OR Vx, Vy - VX := VX OR VY
                ####print(f"Executando OR Vx, Vy - OR entre VX ({self.registers[x]}) e VY ({self.registers[y]})")
                self.registers[x] |= self.registers[y]
            elif n == 0x2:  # AND Vx, Vy - VX := VX AND VY
                ####print(f"Executando AND Vx, Vy - AND entre VX ({self.registers[x]}) e VY ({self.registers[y]})")
                self.registers[x] &= self.registers[y]
            elif n == 0x3:  # XOR Vx, Vy - VX := VX XOR VY
                ####print(f"Executando XOR Vx, Vy - XOR entre VX ({self.registers[x]}) e VY ({self.registers[y]})")
                self.registers[x] ^= self.registers[y]
            elif n == 0x4:  # ADD Vx, Vy - VX := VX + VY, VF := Carry
                sum_val = self.registers[x] + self.registers[y]
                ####print(f"Executando ADD Vx, Vy - Somando VX ({self.registers[x]}) e VY ({self.registers[y]})")
                self.registers[0xF] = 1 if sum_val > 255 else 0
                self.registers[x] = sum_val & 0xFF
            
            elif n == 0x5:  # SUB Vx, Vy - VX := VX - VY, VF := Não houve empréstimo
                ####print(f"Executando SUB Vx, Vy - Subtraindo VX ({self.registers[x]}) de VY ({self.registers[y]})")
                self.registers[0xF] = 1 if self.registers[x] > self.registers[y] else 0
                self.registers[x] = (self.registers[x] - self.registers[y]) & 0xFF
            
            elif n == 0x6:  # SHR Vx - VX := VX >> 1, VF := Bit Menos Significativo
                ####print(f"Executando SHR Vx - Deslocando VX ({self.registers[x]}) para a direita")
                self.registers[0xF] = self.registers[x] & 0x1
                self.registers[x] >>= 1
            elif n == 0x7:  # SUBN Vx, Vy - VX := VY - VX, VF := Not Borrow
                ####print(f"Executando SUBN Vx, Vy - Subtraindo VY ({self.registers[y]}) de VX ({self.registers[x]})")
                self.registers[0xF] = 1 if self.registers[y] > self.registers[x] else 0
                self.registers[x] = (self.registers[y] - self.registers[x]) & 0xFF
            elif n == 0xE:  # SHL Vx - VX := VX << 1, VF := MSB de VX antes do shift
                ####print(f"Executando SHL Vx - Deslocando VX ({self.registers[x]}) para a esquerda")
                self.registers[0xF] = (self.registers[x] >> 7) & 0x1
                self.registers[x] = (self.registers[x] << 1) & 0xFF

        elif first_nibble == 0x9 and n == 0x0:  # SNE Vx, Vy - Pula se VX != VY
            ####print(f"Executando SNE Vx, Vy - Comparando VX ({self.registers[x]}) com VY ({self.registers[y]})")
            if self.registers[x] != self.registers[y]:
                self.pc += 2

        elif first_nibble == 0xA:  # LD I, addr - I := NNN
            ####print(f"Executando LD I, addr - Atribuindo {hex(nnn)} a I")
            self.index_register = nnn
        elif first_nibble == 0xB:  # JP V0, addr - PC := NNN + V0
            ####print(f"Executando JP V0, addr - Pula para {hex(nnn + self.registers[0])}")
            self.pc = nnn + self.registers[0]
        elif first_nibble == 0xC:  # RND Vx, NN - VX := Rand() & NN
            ####print(f"Executando RND Vx, NN - Gerando número aleatório e fazendo AND com {nn}")
            self.registers[x] = random.randint(0, 255) & nn
        elif first_nibble == 0xD:  # DRW Vx, Vy, N - Desenha sprite
            ####print(f"Executando DRW Vx, Vy, N - Desenhando sprite a partir de I com N={n}")
            sprite = self.memory.read_memory(self.index_register, n)
            collision = self.display.draw_sprite(self.registers[x], self.registers[y], sprite)
            self.registers[0xF] = 1 if collision else 0  # VF = 1 se houve colisão, senão 0
        
        elif first_nibble == 0xE0:
                if opcode == 0xE09E:  # EX9E - Skip if key is pressed
                    print(f"Executando 0xE09E - Lendo V0..VX da memória a partir de I")
                    key = self.registers[x]  # Key stored in Vx
                    if self.keypad.is_key_pressed(key):  # Check if key is pressed
                        self.pc += 2  # Skip the next instruction

                elif opcode == 0xE0A1:  # EXA1 - Skip if key is not pressed
                    print(f"Executando 0xE0A1 - Lendo V0..VX da memória a partir de I")
                    key = self.registers[x]  # Key stored in Vx
                    if not self.keypad.is_key_pressed(key):  # Check if key is not pressed
                        self.pc += 2  # Skip the next instruction


        elif first_nibble == 0xF:
            if nn == 0x07:  # FX07 - VX := Delay Timer
                ####print(f"Executando FX07 - Atribuindo o valor do Delay Timer ({self.delay_timer}) a VX")
                self.registers[x] = self.delay_timer
            elif nn == 0x15:  # FX15 - Delay Timer := VX
                ###print(f"Executando FX15 - Atribuindo o valor de VX ({self.registers[x]}) ao Delay Timer")
                self.delay_timer = self.registers[x]
            elif nn == 0x1E:  # FX1E - I := I + VX
                ###print(f"Executando FX1E - Incrementando I com o valor de VX ({self.registers[x]})")
                self.index_register += self.registers[x]
            elif nn == 0x29:  # FX29 - I := Localização do dígito de VX
                ###print(f"Executando FX29 - Definindo I para o dígito de VX ({self.registers[x]})")
                self.index_register = self.registers[x] * 5
            elif nn == 0x55:  # FX55 - Armazena V0..VX na memória a partir de I
                ###print(f"Executando FX55 - Armazenando V0..VX na memória a partir de I")
                for i in range(x + 1):
                    self.memory.write_byte(self.index_register + i, self.registers[i])
            elif nn == 0x65:  # FX65 - Lê V0..VX da memória a partir de I
                ###print(f"Executando FX65 - Lendo V0..VX da memória a partir de I")
                for i in range(x + 1):
                    self.registers[i] = self.memory.read_byte(self.index_register + i)

            elif opcode == 0xF00A:  # FX0A - Wait for key press
                print(f"Executando 0xF00A - Lendo V0..VX da memória a partir de I")
                key = self.keypad.wait_for_key_press()  # Block and wait for key press
                self.registers[x] = key  # Store the key value in Vx
                # No PC increment here since it's waiting for key input
        elif opcode & 0xF0FF == 0xE09E:  # EX9E - Skip if key in VX is pressed
            x = (opcode & 0x0F00) >> 8   # Extrai o registrador X
            if self.keypad.is_key_pressed(self.registers[x]):  # Verifica se a tecla está pressionada
                self.pc += 2  # Pula a próxima instrução

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
        """Verifica e atualiza o estado das teclas pressionadas."""
        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_QUIT:
                self.running = False  # Handle window close event

            if event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym in self.keypad.keymap:
                    #print(f"Key {event.key.keysym.sym} pressed")
                    self.keypad.update_key_state(event.key.keysym.sym, True)  # Key pressed
            elif event.type == sdl2.SDL_KEYUP:
                if event.key.keysym.sym in self.keypad.keymap:
                    #print(f"Key {event.key.keysym.sym} released")
                    self.keypad.update_key_state(event.key.keysym.sym, False)  # Key released






# Testando o emulador com timers
if __name__ == "__main__":
    chip8 = Chip8()

    #chip8.memory.select_rom('res/rom/test_opcode.ch8')
    #chip8.memory.select_rom('res/rom/BC_test.ch8')
    #chip8.memory.select_rom('res/rom/Keypad Test [Hap, 2006].ch8')
    
    #chip8.memory.select_rom('res/rom/ibm-logo.ch8')
    #chip8.memory.dump_memory(0x200, 0x1000)

    

    #chip8.memory.select_rom('res/rom/CAVE')
    chip8.memory.select_rom('res/rom/PONG')
    #chip8.memory.select_rom('res/rom/TANK')
    #chip8.memory.select_rom('res/rom/TETRIS')


    chip8.run()
