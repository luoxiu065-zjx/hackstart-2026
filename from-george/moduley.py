import pygame

class TextInput:
    def __init__(self, position):
        self.base_font = pygame.font.Font(None, 40)
        self.user_text = ''
        self.input_rect = pygame.Rect(position[0], position[1], 150, 50)
        
        self.visible = True
        self.complete = False
    
    #user input to change user_text
    def run_a_frame(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.user_text = self.user_text[:-1]
            elif event.key == pygame.K_DELETE:
                self.user_text = ''
            elif event.key == pygame.K_RETURN:
                self.complete = True
            else:
                self.user_text += event.unicode
        
    
    def draw(self, screen):
        pygame.draw.rect(screen, "#333333", self.input_rect)
        #create text surface
        self.text_surface = self.base_font.render(self.user_text, True, (255, 255, 255))
        #draw text surface
        screen.blit(self.text_surface, (self.input_rect.x+5, self.input_rect.y+10))
        #update rect to match text width
        self.input_rect.w = max(100, self.text_surface.get_width()+10)