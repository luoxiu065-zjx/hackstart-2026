import pygame

import moduley

class Question:
    def __init__(self, title, number):
        self.title = title
        self.number = number

class Q_TextInput(Question):
    def __init__(self, title, number):
        Question.__init__(self, title, number)
        self.input = moduley.TextInput([100, 100])



def cancel_survey():
    #complete true actions - probably do seperately, store true_action_list
    #cancellation survey
    #shrinking exit
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    running = True

    q12 = Q_TextInput("words", 5)

    while running:
        event_list = pygame.event.get()
        event_list.append(pygame.event.Event(pygame.NOEVENT, dict=None))
        for event in event_list:
            #closes window
            if event.type == pygame.QUIT:
                running = False

            q12.input.run_a_frame(event)

            screen.fill("white")

            q12.input.draw(screen)

            pygame.display.flip()
            clock.tick(60)
    pygame.quit()

cancel_survey()