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

    def update_key_state(self, key_code, state):
        """Atualiza o estado de uma tecla (pressionada ou solta)."""
        if key_code in self.keymap:
            key = self.keymap[key_code]
            self.keys[key] = 1 if state else 0

    def is_key_pressed(self, chip8_key):
        """Retorna True se a tecla correspondente do CHIP-8 estiver pressionada."""
        return self.keys[chip8_key] == 1


    def wait_for_key_press(self):
        """Espera até que uma tecla seja pressionada e retorna o código da tecla."""
        while True:
            for event in sdl2.ext.get_events():
                if event.type == sdl2.SDL_QUIT:
                    self.running = False  # Handle window close event
                if event.type == sdl2.SDL_KEYDOWN:
                    key = event.key.keysym.sym
                    if key in self.keymap:
                        return self.keymap[key]  # Return the mapped key
