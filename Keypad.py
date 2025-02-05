import sdl2

class Keypad:
    def __init__(self):
        """Inicializa o teclado com 16 teclas do CHIP-8."""
        self.keys = [0] * 16  # Estado das teclas (0 = solta, 1 = pressionada)

        # Mapeamento de teclas SDL2 para os valores do CHIP-8
        self.keymap = {
            sdl2.SDLK_1: 0x1, sdl2.SDLK_2: 0x2, sdl2.SDLK_3: 0x3, sdl2.SDLK_4: 0xC,
            sdl2.SDLK_q: 0x4, sdl2.SDLK_w: 0x5, sdl2.SDLK_e: 0x6, sdl2.SDLK_r: 0xD,
            sdl2.SDLK_a: 0x7, sdl2.SDLK_s: 0x8, sdl2.SDLK_d: 0x9, sdl2.SDLK_f: 0xE,
            sdl2.SDLK_z: 0xA, sdl2.SDLK_x: 0x0, sdl2.SDLK_c: 0xB, sdl2.SDLK_v: 0xF
        }

    def handle_event(self, event):
        """Lida com eventos de teclado do SDL2."""
        if event.type == sdl2.SDL_KEYDOWN:
            if event.key.keysym.sym in self.keymap:
                self.keys[self.keymap[event.key.keysym.sym]] = 1  # Pressionada

        elif event.type == sdl2.SDL_KEYUP:
            if event.key.keysym.sym in self.keymap:
                self.keys[self.keymap[event.key.keysym.sym]] = 0  # Solta

    def is_key_pressed(self, chip8_key):
        """Retorna True se a tecla correspondente do CHIP-8 estiver pressionada."""
        return self.keys[chip8_key] == 1
