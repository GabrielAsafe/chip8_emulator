import sdl2
import sdl2.ext
import numpy as np

class Chip8Display:
    def __init__(self, scale=10):
        self.width = 64
        self.height = 32
        self.scale = scale
        self.screen = np.zeros((self.height, self.width), dtype=np.uint8)

        # Inicializa SDL2
        sdl2.ext.init()
        self.window = sdl2.ext.Window("CHIP-8 Emulator", size=(self.width * self.scale, self.height * self.scale))
        self.window.show()

        self.renderer = sdl2.ext.Renderer(self.window)
        self.renderer.clear()

    def clear(self):
        """Limpa a tela e atualiza a renderização."""
        self.screen.fill(0)
        self.render()

    def draw_sprite(self, x, y, sprite):
        """Desenha um sprite na posição (x, y) e retorna se houve colisão."""
        collision = False
        for row_index, byte in enumerate(sprite):
            for col_index in range(8):  # Cada byte tem 8 bits (horizontal)
                if (byte >> (7 - col_index)) & 1:  # Verifica se o bit está ligado
                    pixel_x = (x + col_index) % self.width
                    pixel_y = (y + row_index) % self.height

                    if self.screen[pixel_y, pixel_x] == 1:
                        collision = True  # Um pixel aceso foi apagado

                    # XOR (inverte o estado do pixel)
                    self.screen[pixel_y, pixel_x] ^= 1

        self.render()  # Atualiza a tela após desenhar
        return collision

    def render(self):
        """Renderiza a tela no SDL2."""
        self.renderer.clear()
        self.renderer.color = sdl2.ext.Color(0, 0, 0)  # Fundo preto
        self.renderer.fill((0, 0, self.width * self.scale, self.height * self.scale))  # Preenche fundo

        self.renderer.color = sdl2.ext.Color(255, 255, 255)  # Cor branca para pixels ativos

        for y in range(self.height):
            for x in range(self.width):
                if self.screen[y, x]:  # Se o pixel estiver ligado
                    rect = sdl2.SDL_Rect(x * self.scale, y * self.scale, self.scale, self.scale)
                    sdl2.SDL_RenderFillRect(self.renderer.sdlrenderer, rect)

        self.renderer.present()

    def handle_events(self):
        """Gerencia eventos do SDL2."""
        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_QUIT:
                return False
        return True

    def destroy(self):
        """Fecha a janela e encerra o SDL2."""
        self.window.close()
        sdl2.ext.quit()

# Teste da tela
if __name__ == "__main__":
    display = Chip8Display(scale=10)  # Escala de 10x (tela 640x320)

    # Teste: desenha um número "0" na posição (10,5)
    sprite_0 = [0xF0, 0x90, 0x90, 0x90, 0xF0]
    display.draw_sprite(10, 5, sprite_0)

    running = True
    while running:
        running = display.handle_events()  # Mantém a tela aberta e processa eventos

    display.destroy()
