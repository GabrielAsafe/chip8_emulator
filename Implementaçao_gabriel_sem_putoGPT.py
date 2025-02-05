import time
import sdl2.ext
import random
from Timers import Timers
from Keypad import Keypad
from Display import Chip8Display
from Memory import Memory
from Stack import Stack


class Registers:
    def __init__(self):
        self.registers = [0] * 16  # Registradores V0-VF
        self.index_register = 0  # Registrador de índice
        self.pc = 0x200  # Contador de programa (inicia em 0x200)


class Chip8:
    def __init__(self):
        self.memory = Memory()  # Usando a classe Memory
        self.registers = Registers()
        self.stack = Stack()
        self.display = Chip8Display()  # Classe de exibição
        self.timers = Timers()  # Classe de timers
        self.running = True  # Indicador de execução
        self.waiting_for_key = False  # Controle para espera de tecla
        self.display = Chip8Display(scale=15)
        self.logFetch = []
        self.emulationMode = "SUPER-CHIP" #related with instruction BNNN
        self.keypad = Keypad()

    def fetch_opcode(self):
        """Busca o próximo opcode (16 bits) da memória."""
        high_byte = self.memory[self.registers.pc]  # primeiro byte(olhando o hex do programa de teste)
        low_byte = self.memory[self.registers.pc + 1]  # segundo byte
        opcode = (high_byte << 8) | low_byte 
        self.logFetch.append({'high_byte': high_byte, 'low_byte': low_byte, 'opcode': opcode})
        self.registers.pc += 2  # Incrementa o contador de programa
        return  opcode


    def decode_execute(self, opcode):
        """Decodifica e executa a instrução."""
        first_nibble = (opcode & 0xF000) >> 12  
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        n = opcode & 0x000F
        nn = opcode & 0x00FF
        nnn = opcode & 0x0FFF

        print(f"Decodificando opcode: {hex(opcode)}")
        print(f"first_nibble: {first_nibble}, x: {x}, y: {y}, n: {n}, nn: {nn}, nnn: {nnn}")
        

        #We’ll start out with an instruction that you actually don’t want to implement! In the original CHIP-8 interpreters, this would pause execution of the CHIP-8 program and call a subroutine written in machine language at address NNN instead.        This routine would be written in the machine language of the computer’s CPU; on the original COSMAC VIP and the ETI-660, this was 1802 machine code, and on the DREAM 6800, M6800 code. Unless you’re making an emulator for either of those computers, skip this one.
        if opcode == 0x0:
            print("hell naah")

        #This is pretty simple: It should clear the display, turning all pixels off to 0.
        if opcode == 0x00E0:
            self.display.clear()
        
        
        #This instruction should simply set PC to NNN, causing the program to jump to that memory location. Do not increment the PC afterwards, it jumps directly there.
        if opcode == 0x1:  
            self.registers.pc = nnn
        
        #2NNN calls the subroutine at memory location NNN. In other words, just like 1NNN, you should set PC to NNN. However, the difference between a jump and a call is that this instruction should first push the current PC to the stack, so the subroutine can return later.
        # Returning from a subroutine is done with 00EE, and it does this by removing (“popping”) the last address from the stack and setting the PC to it.
        if opcode == 0xEE or opcode == 2 :
            if( opcode == 0x2):
                self.stack.push(self.registers.pc )
                self.registers.pc = nnn
            if( opcode == 0xEE):
                self.stack.pop()
        
        #Or, put another way, they execute the next instruction if and only if the condition is not true. Since these conditional branch instructions can only skip one instruction, they’re usually followed by a jump/call (1NNN/2NNN) instruction which jumps to the actual “if code block” that should be executed if the condition is true.
        #-----
        if opcode == 0x30 : 
            
            if(x== nn):
                self.registers.pc +=1

        if opcode == 0x40 :
            if(x!= nn):
               self.registers.pc +=1

        if opcode == 0x50:
            if(x== nn):
                self.registers.pc +=1
        
        if opcode == 0x90:
            if(x!= nn):
               self.registers.pc +=1
        #-----

        #Simply set the register VX to the value NN.
        if opcode == 0x06: 
            x = nn
        
        #Add the value NN to VX. Note that on most other systems, and even in some of the other CHIP-8 instructions, this would set the carry flag if the result overflowed 8 bits; in other words, if the result of the addition is over 255. For this instruction, this is not the case. If V0 contains FF and you execute 7001, the CHIP-8’s flag register VF is not affected.
        if opcode == 0x7:  
           x +=nn
    
        #Logical and arithmetic instructions
      
        if opcode == 0x8:  
            if n == 0x0:  # 8XY0: Set VX = VY
                self.registers[x] = self.registers[y]

            elif n == 0x1:  # 8XY1: VX |= VY
                self.registers[x] |= self.registers[y]

            elif n == 0x2:  # 8XY2: VX &= VY
                self.registers[x] &= self.registers[y]

            elif n == 0x3:  # 8XY3: VX ^= VY
                self.registers[x] ^= self.registers[y]

            elif n == 0x4:  # 8XY4: VX += VY (with carry flag)
                sum_val = self.registers[x] + self.registers[y]
                self.registers[0xF] = 1 if sum_val > 255 else 0
                self.registers[x] = sum_val & 0xFF  # Keep within 8 bits

            elif n == 0x5:  # 8XY5: VX -= VY (with borrow flag)
                self.registers[0xF] = 1 if self.registers[x] > self.registers[y] else 0
                self.registers[x] = (self.registers[x] - self.registers[y]) & 0xFF

            elif n == 0x7:  # 8XY7: VX = VY - VX (with borrow flag)
                self.registers[0xF] = 1 if self.registers[y] > self.registers[x] else 0
                self.registers[x] = (self.registers[y] - self.registers[x]) & 0xFF

            elif n == 0x6:  # 8XY6: VX >>= 1 (Shift Right, ambiguous behavior)
                self.registers[0xF] = self.registers[x] & 0x1  # Save LSB in VF
                self.registers[x] >>= 1  # Shift right by 1

            elif n == 0xE:  # 8XYE: VX <<= 1 (Shift Left, ambiguous behavior)
                self.registers[0xF] = (self.registers[x] >> 7) & 0x1  # Save MSB in VF
                self.registers[x] = (self.registers[x] << 1) & 0xFF  # Shift left and keep within 8 bits

        
        #This sets the index register I to the value NNN.
        if opcode == 0xA:
            self.registers.index_register = nnn

        #In the original COSMAC VIP interpreter, this instruction jumped to the address NNN plus the value in the register V0. This was mainly used for “jump tables”, to quickly be able to jump to different subroutines based on some input.
        #Starting with CHIP-48 and SUPER-CHIP, it was (probably unintentionally) changed to work as BXNN: It will jump to the address XNN, plus the value in the register VX. So the instruction B220 will jump to address 220 plus the value in the register V2.
        #The BNNN instruction was not widely used, so you might be able to just implement the first behavior (if you pick one, that’s definitely the one to go with). If you want to support a wide range of CHIP-8 programs, make this “quirk” configurable.
        if opcode == 0xB:
            if self.emulationMode == "COSMAC_VIP":
                self.pc = nnn + self.registers[0]  # Jump to NNN + V0
            elif self.emulationMode == "SUPER-CHIP":
                self.pc = (x << 8) + nn + self.registers[x]  # Jump to XNN + VX
        #This instruction generates a random number, binary ANDs it with the value NN, and puts the result in VX.
        if opcode == 0xC:
            self.registers[x] = random.randint(0, 255) & nn  # Generates a random 8-bit number and ANDs it with NN


        #alan turing crys in programming (aqui foi com o puto gpt)
        if opcode == 0xD:
            x_cord = self.registers[x] & 63  # X wraps at 64
            y_cord = self.registers[y] & 31  # Y wraps at 32
            height = n  # Number of sprite rows
            self.registers[0xF] = 0  # Reset collision flag

            for row in range(height):
                sprite_byte = self.memory.read_byte(self.index_register + row)  # Read sprite row from memory
                for col in range(8):
                    pixel = (sprite_byte >> (7 - col)) & 1  # Extract individual pixel bit
                    if pixel:  # Only draw if pixel is 'on'
                        if self.display.toggle_pixel(x_cord + col, y_cord + row):  
                            self.registers[0xF] = 1  # Set collision flag if pixel was already on

        if opcode == 0xE09E:
            if self.keypad.is_key_pressed(self.registers[x]):
                self.registers.pc += 2

        if opcode == 0xE0A1:
            if not self.keypad.is_key_pressed(self.registers[x]):
                self.registers.pc += 2

        elif first_nibble == 0xF:
            if nn == 0x07:  # FX07 - VX := Delay Timer
                print(f"Executando FX07 - Atribuindo o valor do Delay Timer ({self.delay_timer}) a VX")
                self.registers[x] = self.delay_timer
            elif nn == 0x15:  # FX15 - Delay Timer := VX
                print(f"Executando FX15 - Atribuindo o valor de VX ({self.registers[x]}) ao Delay Timer")
                self.delay_timer = self.registers[x]
            elif nn == 0x1E:  # FX1E - I := I + VX
                print(f"Executando FX1E - Incrementando I com o valor de VX ({self.registers[x]})")
                self.index_register += self.registers[x]
            elif nn == 0x29:  # FX29 - I := Localização do dígito de VX
                print(f"Executando FX29 - Definindo I para o dígito de VX ({self.registers[x]})")
                self.index_register = self.registers[x] * 5
            elif nn == 0x55:  # FX55 - Armazena V0..VX na memória a partir de I
                print(f"Executando FX55 - Armazenando V0..VX na memória a partir de I")
                for i in range(x + 1):
                    self.memory.write_byte(self.index_register + i, self.registers[i])
            elif nn == 0x65:  # FX65 - Lê V0..VX da memória a partir de I
                print(f"Executando FX65 - Lendo V0..VX da memória a partir de I")
                for i in range(x + 1):
                    self.registers[i] = self.memory.read_byte(self.index_register + i)

        
        
        
    def handle_events(self):
        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_QUIT:
                self.running = False  # Handle window close event

            if event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym in self.keymap:
                    self.keys[self.keymap[event.key.keysym.sym]] = 1  # Key pressed

            elif event.type == sdl2.SDL_KEYUP:
                if event.key.keysym.sym in self.keymap:
                    self.keys[self.keymap[event.key.keysym.sym]] = 0  # Key released

    def run(self):
        while self.registers.pc < 0x500:
            opcode = self.fetch_opcode()  # Busca o próximo opcode
            
            self.decode_execute(opcode)  # Decodifica e executa a instrução
            self.display.render()  # Atualiza a tela
            self.handle_events()  # Lida com eventos (ex: janela fechando)
            time.sleep(1/700)  # Aproximadamente 700 instruções por segundo


# Testando o emulador com timers
if __name__ == "__main__":
    chip8 = Chip8()

    chip8.memory.select_rom('res/rom/test_opcode.ch8')

    #chip8.memory.select_rom('res/rom/BC_test.ch8')
    

    #chip8.memory.select_rom('res/rom/ibm-logo.ch8')
    #chip8.memory.dump_memory(0x200, 0x1000)
    

    #chip8.memory.select_rom('res/rom/CAVE')
    #chip8.memory.select_rom('res/rom/PONG')
    #chip8.memory.select_rom('res/rom/TANK')
    #chip8.memory.select_rom('res/rom/TETRIS')


    chip8.run()
