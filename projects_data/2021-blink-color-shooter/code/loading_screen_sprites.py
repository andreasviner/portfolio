import pygame
WHITE = (255, 225, 255)
 
class arrow(pygame.sprite.Sprite):
    #This class represents a car. It derives from the "Sprite" class in Pygame.
    
    def __init__(self, color, size):
        self.color = (255,255,0)
        self.size = size
        # Call the parent class (Sprite) constructor
        super().__init__()
        
        # Pass in the color of the car, and its x and y position, width and height.
        # Set the background color and set it to be transparent
        self.image = pygame.Surface([size*2, size*2])
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)
        
 
        pygame.draw.polygon(self.image, color=self.color, points=[(size//2,size//2+size//4), (size,size//2+size//4), (size,size//2),(size//2+size,size),(size,size//2+size),(size,size//2+(size//4)*3),(size//2,size//2+(size//4)*3)])        # Fetch the rectangle object that has the dimensions of the image.
        self.rect = self.image.get_rect()
    def rotate(self, degrees):
        size = self.size
        self.image = pygame.Surface([size*2, size*2])
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)
        
 
        pygame.draw.polygon(self.image, color=self.color, points=[(size//2,size//2+size//4), (size,size//2+size//4), (size,size//2),(size//2+size,size),(size,size//2+size),(size,size//2+(size//4)*3),(size//2,size//2+(size//4)*3)])        # Fetch the rectangle object that has the dimensions of the image.

        self.image = pygame.transform.rotate(self.image, degrees)

    def update_color(self, color):
        self.color = color
