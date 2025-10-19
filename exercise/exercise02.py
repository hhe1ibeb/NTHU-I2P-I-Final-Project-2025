'''
Exercise 2: Hello Green

Task:
<<<<<<< HEAD
<<<<<<< HEAD
- Successfully update the screen to become green and red
=======
- Successfully render the screen to become green
>>>>>>> 6826c16 (spec)
=======
- Successfully update the screen to become green and red
>>>>>>> 4a428cd (spec & exercise)
- python exercise/exercise02.py
'''
import pygame

pygame.init()

screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Hello Green")

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
    
<<<<<<< HEAD
<<<<<<< HEAD
    pygame.time.wait(10)
    screen.fill((0, 255, 0))
    '''TODO: Flip Display'''
    
    pygame.time.wait(10)
    screen.fill((255, 0, 0))
    '''TODO: Flip Display'''
=======
    screen.fill((0, 255, 0))
    pygame.display.flip()
>>>>>>> 6826c16 (spec)
=======
    pygame.time.wait(10)
    screen.fill((0, 255, 0))
    '''TODO: Flip Display'''
    
    pygame.time.wait(10)
    screen.fill((255, 0, 0))
    '''TODO: Flip Display'''
>>>>>>> 4a428cd (spec & exercise)
         
         