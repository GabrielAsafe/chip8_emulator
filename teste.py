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
        
        if opcode == 0x00E0:  # CLS - Limpa a tela
            print("Executando CLS - Limpa a tela")
            self.display.clear()
        if opcode == 0x1nnn:  # CLS - Limpa a tela
            print("Executando CLS - Limpa a tela")
            self.display.clear()
        if opcode == 0x6xnn :  # CLS - Limpa a tela
            print("Executando CLS - Limpa a tela")
            self.display.clear()
        if opcode == 0x7xnn:  # CLS - Limpa a tela
            print("Executando CLS - Limpa a tela")
            self.display.clear()
        if opcode == 0xAnnn:  # CLS - Limpa a tela
            print("Executando CLS - Limpa a tela")
            self.display.clear()
        if opcode == 0xdxyn:  # CLS - Limpa a tela
            print("Executando CLS - Limpa a tela")
            self.display.clear()


    def run(self):
        while self.registers.pc < 0x500:
            opcode = self.fetch_opcode()  # Busca o próximo opcode
            
            self.decode_execute(opcode)  # Decodifica e executa a instrução
            #self.display.render()  # Atualiza a tela
            #self.handle_events()  # Lida com eventos (ex: janela fechando)
            #time.sleep(1/700)  # Aproximadamente 700 instruções por segundo
if __name__ == '__main__':
    chip8 = Chip8()

    chip8.memory.select_rom('res/rom/ibm-logo.ch8')

    #chip8.memory.select_rom('res/rom/BC_test.ch8')
    #chip8.memory.select_rom('res/rom/CAVE')

    #chip8.memory.dump_memory(0x200, 0x1000)


    
    chip8.run()