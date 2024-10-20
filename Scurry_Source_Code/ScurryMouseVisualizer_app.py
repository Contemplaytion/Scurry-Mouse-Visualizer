import time
import math
import os
import sys
import threading

import pygame
from pynput import mouse

#NOTE: BE. SURE. ENHANCE POINTER PRECISION. IS. TURNED. OFF. PERIOD. (Windows)

#KNOWN ISSUE: Grabbing the app and dragging it along the screen does not play nice with the pynput mouse.Listener() object and causes severe lag for a few seconds before some timeout.
#CAUTION: I do not recommend running this app at high framerate because the cpu utilization may impact your game. I recommend keeping it at 60 FPS because that's the framerate most people will be viewing your gameplay will see.

#INITIALIZE GLOBAL VARIABLES
#NOTE:  To prevent unintended code execution when importing this script, I have decided to use a function to declare all global variables and constants
#       required for this script to run. For actual documentation on the function of these variables, see the initialize() function

def initialize(config_as_dictionary=None): #INITIALIZE ALL GLOBAL VARIABLES from here to prevent unintended code execution if this function is imported
    
    #GLOBAL CONSTANTS
    global CURRENT_PROFILE, APP_WINDOW_HEIGHT, APP_WINDOW_WIDTH, INITIAL_SPRITE_POSITION, BACKGROUND_COLOR, FPS, UPPER_X_BOUNDARY, UPPER_Y_BOUNDARY, LOWER_X_BOUNDARY, LOWER_Y_BOUNDARY 
    global DISABLE_MOVEMENT_IF_CURSOR_LEAVES_BOUNDARIES, CENTERED_CURSOR_MODE, CENTER_SCREEN_POS, SENSITIVITY, TRAIL_LIFETIME,ENABLE_CURSOR_IDLE_RESET, CURSOR_IDLE_RESET
    global WRAPPING_MODE, TRAIL_THICKNESS, VELOCITY_SMOOTHING, TRAIL_SAMPLE_RATE, TRAIL_DOT_SPAWN_COOLDOWN, CIRCLE_SPRITE_SIZE, CIRCLE_SPRITE_COLOR, CIRCLE_OUTLINE_SIZE, CIRCLE_OUTLINE_COLOR
    global USE_CUSTOM_SPRITE, CUSTOM_SPRITE_SIZE, CUSTOM_SPRITE_FILEPATH, ANIMATE_SPRITE, ANIMATION_SPEED, ROTATE_SPRITE, DRAW_MOUSE_SPRITE, DRAW_TRAIL_DOTS, DRAW_TRAIL_LINES
    global SLOW_TRAIL_COLOR, MEDIUM_FAST_TRAIL_COLOR, VERY_FAST_TRAIL_COLOR, SLOW_COLOR_UPPER_BOUNDARY, MEDIUM_FAST_COLOR_LOWER_BOUNDARY, MEDIUM_FAST_COLOR_UPPER_BOUNDARY, VERY_FAST_COLOR_LOWER_BOUNDARY
    
    #GLOBAL VARIABLES
    global cursor, cursor_pos, prev_x, prev_y, prev_velocities, last_update_time, prev_trail_dot, moving, moving_x, moving_y, buffer_x, buffer_y
    global clock, screen, mouse_sprite, mouse_sprite_group, trail_dot_group, moving_lock, wrapping_lock
    
    if not config_as_dictionary:
        
        #STANDALONE CONFIGURATION:
        #If you are running this script stand-alone (as in if __name__ == "__main__"), edit this dictionary to set config parameters.
        #See below where global constants are assigned values for additional documentation on each parameter
        
        #my personal testing config. change this to fit your needs.
        STANDALONE_RUNTIME_CONFIG = {
            'profile_name' : 'STANDALONE',

            'app_window_width': 800,
            'app_window_height' : 600, 
            'background_color' : (50, 50, 50), 
            'fps' : 60, 

            'lower_x_boundary' : 0, 
            'upper_x_boundary' : 2560, 
            'lower_y_boundary' : 0, 
            'upper_y_boundary' : 1440, 

            'centered_cursor_mode' : False, 

            'sensitivity' : 0.15,
            'trail_lifetime' : 0.5, 
            'enable_cursor_idle_reset' : True, 
            'cursor_idle_reset' : 0.5, 
            'wrapping_mode' : False, 

            'trail_thickness' : 8, 
            'trail_sample_rate' : 250,
            'velocity_smoothing' : 2, 

            'circle_sprite_size' : 16, 
            'circle_sprite_color' : (255, 255, 255), 
            'circle_outline_size' : 2, 
            'circle_outline_color' : (0, 0, 0), 

            'use_custom_sprite' : True, 
            'custom_sprite_size' : 50, 
            'custom_sprite_filepath' : './Assets/Default_Mouse_Sprite_Sheet.png',

            'rotate_sprite' : True,
            'animate_sprite' : True, 
            'animation_speed' : 0.4,

            'draw_mouse_sprite' : True, 
            'draw_trail_dots' : False, 
            'draw_trail_lines' : True, 

            'slow_trail_color' : (255, 0, 0), 
            'medium_fast_trail_color' : (255, 255, 0), 
            'very_fast_trail_color' : (125, 125, 255), 

            'slow_color_upper_boundary' : 30, 
            'medium_fast_color_lower_boundary' : 40, 
            'medium_fast_color_upper_boundary' : 50, 
            'very_fast_color_lower_boundary' : 80 
        }
        
        config_as_dictionary = STANDALONE_RUNTIME_CONFIG

    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #LOAD CONFIG PARAMETER VALUES

    CURRENT_PROFILE = config_as_dictionary['profile_name'] #User can save custom config profiles and give them names using the Scurry Launcher. This parameter can tell the user at a glance which profile the settings were taken from
    
    APP_WINDOW_WIDTH = config_as_dictionary['app_window_width']
    APP_WINDOW_HEIGHT = config_as_dictionary['app_window_height']
    INITIAL_SPRITE_POSITION = (APP_WINDOW_WIDTH // 2, APP_WINDOW_HEIGHT // 2)
    BACKGROUND_COLOR = config_as_dictionary['background_color'] #screen background color. Intended to be used for chroma key when capturing in OBS.
    FPS = config_as_dictionary['fps']

    # Scurry will assume that your mouse cursor is confined to these boundaries by your game/application. 
    # It is extremely important that these are measured accurately, as scurry needs to know the exact dimensions of 
    # the window to perform the logic for projecting mouse movements beyond the window border
    LOWER_X_BOUNDARY = config_as_dictionary['lower_x_boundary']
    UPPER_X_BOUNDARY = config_as_dictionary['upper_x_boundary']
    LOWER_Y_BOUNDARY = config_as_dictionary['lower_y_boundary'] 
    UPPER_Y_BOUNDARY = config_as_dictionary['upper_y_boundary']

    DISABLE_MOVEMENT_IF_CURSOR_LEAVES_BOUNDARIES = True #Togglable for debug purposes...and for your sanity. Disable at your own risk.

    CENTERED_CURSOR_MODE = config_as_dictionary['centered_cursor_mode'] #Enable if the game being played traps the cursor in the center of the screen
    CENTER_SCREEN_POS = ((LOWER_X_BOUNDARY + UPPER_X_BOUNDARY - 1) / 2, (LOWER_Y_BOUNDARY + UPPER_Y_BOUNDARY - 1) / 2 ) #Used for calculating movements for games that lock the cursor in the center of the screen
    #Through my experimental testing, I've learned that it is very important that floating point division is used here, and not integer division.

    SENSITIVITY = config_as_dictionary['sensitivity'] #Used to adjust how far the sprite moves relative to each mouse movement
    TRAIL_LIFETIME = config_as_dictionary['trail_lifetime'] #Number of seconds the trailing effect will capture
    ENABLE_CURSOR_IDLE_RESET = config_as_dictionary['enable_cursor_idle_reset']
    CURSOR_IDLE_RESET = config_as_dictionary['cursor_idle_reset'] #If a mouse move is not detected for this amount of time, the mouse sprite will be reset to it's initial position.
    WRAPPING_MODE = config_as_dictionary['wrapping_mode'] #Used to decide what happens when the mouse sprite leaves the window. If true, the sprite will wrap to the opposite edge. If false, the sprite will respawn in it's initial position.

    TRAIL_THICKNESS = config_as_dictionary['trail_thickness'] #measured in pixels
    TRAIL_SAMPLE_RATE = config_as_dictionary['trail_sample_rate'] #The maximum number of times per second that the mouse cursor position is sampled to create a trail dot.
    try: TRAIL_DOT_SPAWN_COOLDOWN = round(1 / abs(TRAIL_SAMPLE_RATE), 3) #The minimum amount of time in seconds that passes between each trail dot spawn.
    except ZeroDivisionError:TRAIL_DOT_SPAWN_COOLDOWN = 0.004 #default value

    #Mouse Velocity is quite volatile and changes somewhat erratically moment to moment. Therefore it is a good idea to smooth out the velocity curve by computing a moving average of current velocity and previous velocities
    VELOCITY_SMOOTHING = config_as_dictionary["velocity_smoothing"] #Must be an integer 0 - 9. Will be used to determine how many points are used to create the moving average mentioned above.

    CIRCLE_SPRITE_SIZE = config_as_dictionary['circle_sprite_size'] #Size of circle sprite DIAMETER, not radius
    CIRCLE_SPRITE_COLOR = config_as_dictionary['circle_sprite_color']
    CIRCLE_OUTLINE_SIZE = config_as_dictionary['circle_outline_size'] #User can give the circle sprite a colored outline to improve visabilty against varying backgrounds
    CIRCLE_OUTLINE_COLOR = config_as_dictionary['circle_outline_color'] 

    USE_CUSTOM_SPRITE = config_as_dictionary['use_custom_sprite'] #CUSTOM MOUSE SPRITES MUST BE PIXEL-PERFECT SQUARES. Else, the program will scale your sprite to fit a square.
    CUSTOM_SPRITE_SIZE = config_as_dictionary['custom_sprite_size'] #Custom sprites will be scaled to fit a square with this value as the side length.
    CUSTOM_SPRITE_FILEPATH = config_as_dictionary['custom_sprite_filepath']

    if CUSTOM_SPRITE_FILEPATH[-4:] != ".png" or os.path.exists(CUSTOM_SPRITE_FILEPATH) == False: #Dead/invalid filepath protection
        USE_CUSTOM_SPRITE = False
    
    ROTATE_SPRITE = config_as_dictionary['rotate_sprite'] #Enable if you want the sprite to rotate in the direction of your mouse movement. It is important that your custom sprite faces to the right if you enable this setting.
    ANIMATE_SPRITE = config_as_dictionary['animate_sprite'] #Enable if you have a valid sprite sheet to use for an animated sprite. THE SPRITE SHEET MUST CONTAIN PIXEL-PERFECT SQUARE FRAMES THAT ARE POSITIONED HORIZONTALLY IN ORDER WITH NO SPACERS IN BETWEEN.
    ANIMATION_SPEED = config_as_dictionary['animation_speed'] #Measured in seconds / frame

    DRAW_MOUSE_SPRITE = config_as_dictionary['draw_mouse_sprite'] #Disable this if you would rather just see the trailing effect as a representation of your mouse movements
    DRAW_TRAIL_DOTS = config_as_dictionary['draw_trail_dots'] #Togglable to allow users to decide which asthetic they prefer for the trail effect
    DRAW_TRAIL_LINES = config_as_dictionary['draw_trail_lines'] #^^^
    #Disabling all 3 of these is.... well......not really reccommnended. It will essentially turn Scurry into the computer version of a paperweight. But, I mean, you do you.

    #Configurable Trail Colors
    SLOW_TRAIL_COLOR = config_as_dictionary['slow_trail_color']
    MEDIUM_FAST_TRAIL_COLOR = config_as_dictionary['medium_fast_trail_color']
    VERY_FAST_TRAIL_COLOR = config_as_dictionary['very_fast_trail_color']

    #Configurable speeds associated with trail colors. Essentially, these must be values between 0 and 100, and must be in ascending order.
    #More thorough documentation can be found in the Trail_Dot.get_color() method
    SLOW_COLOR_UPPER_BOUNDARY = config_as_dictionary['slow_color_upper_boundary']
    MEDIUM_FAST_COLOR_LOWER_BOUNDARY = config_as_dictionary['medium_fast_color_lower_boundary']
    MEDIUM_FAST_COLOR_UPPER_BOUNDARY = config_as_dictionary['medium_fast_color_upper_boundary']
    VERY_FAST_COLOR_LOWER_BOUNDARY = config_as_dictionary['very_fast_color_lower_boundary']
    
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #INITIALIZE GLOBAL VARIABLES
    cursor = mouse.Controller() 
    
    cursor_pos = cursor.position #is continually updated by the on_move() function to store the most recent location of the mouse cursor (independent of cursor boundaries)
    # It is importaant to note that cursor_pos and cursor.position are function completely separately and independently in this program. the statement above is merely to give cursor_pos an initial value
    # cursor_pos will be used to store position data received by the mouse.Listener() object, while cursor.position is an attribute of the mouse.Controller() object.

    prev_x = cursor_pos[0] #used for computing mouse velocity
    prev_y = cursor_pos[1]
    last_update_time = (time.time(), time.time()) #stores timestamps in the format (x update time, y update time)
    prev_velocities = [] #used to store previous velocity values to compute moving average
    
    if int(VELOCITY_SMOOTHING) > 0:
        for i in range(VELOCITY_SMOOTHING):
            prev_velocities.append(0)
    
    prev_trail_dot = (prev_x, prev_y ,time.time()) #tracks the x, y, and init time of most revently created trail dot. used for velocity calculations.
    #I chose to use a tuple to store these because I learned that tuples are faster than lists, but now that I've seen how fast the code actually needs to be I'm not sure that this is an optimization that actually matters.
    
    moving = False
    moving_x = False
    moving_y = False

    buffer_x = 0
    buffer_y = 0

    # Initialize pygame
    pygame.init()
    clock = pygame.time.Clock()

    # Set up display
    screen = pygame.display.set_mode((APP_WINDOW_WIDTH, APP_WINDOW_HEIGHT))

    try:
        icon = pygame.image.load("Assets/MouseIcon.png")
        pygame.display.set_icon(icon)
    except:
        pass #pygame icon will be loaded by default
    
    try:
        if config_as_dictionary['profile_name'] in {"DEFAULT",  "NONE"}:
            profile = ""
        else:
            profile = '[' + config_as_dictionary['profile_name'] + ']'
    except:
        profile = ""

    if __name__ == "__main__":
        pygame.display.set_caption(f"Scurry Mouse Visualizer{profile}")
    else:
        pygame.display.set_caption(f"Scurry Mouse Visualizer{profile} (Press 'Esc' to Configure)")

    #CREATE GAME OBJECTS
    mouse_sprite = Mouse_Sprite(INITIAL_SPRITE_POSITION[0], INITIAL_SPRITE_POSITION[1])
    mouse_sprite_group = pygame.sprite.Group()
    mouse_sprite_group.add(mouse_sprite)
    trail_dot_group = pygame.sprite.Group()

    # Use threading locks to safely access/modify shared variables
    moving_lock = threading.Lock() #used for daemon threads to safely access the last_update_time global variable
    wrapping_lock = threading.Lock() #used to ensure that trail lines cleanly break on opposite sides of the screen if the sprite wraps from one side to the other

#DEFINE GAME OBJECTS
class Mouse_Sprite(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.float_x = float(x) #best to use floating point numbers for position and velocity calculations, then round to nearest integer when drawing to the screen
        self.float_y = float(y)

        self.wrapped_last_frame = False #used to tell Scurry when NOT to draw lines connecting two trail dots

        if USE_CUSTOM_SPRITE:
            sprite_sheet = pygame.image.load(CUSTOM_SPRITE_FILEPATH) #use instance variable to allow for loading large files that do not persist after scaling to smaller size.
            sprite_sheet_width = sprite_sheet.get_width()
            sprite_sheet_height = sprite_sheet.get_height()

            if sprite_sheet_width % sprite_sheet_height == 0: #sprite sheet consists of square frames ordered horizontally
                num_frames = sprite_sheet_width // sprite_sheet_height
            else:
                num_frames = 1
              
            self.sprite_sheet = pygame.transform.scale(sprite_sheet,(num_frames * CUSTOM_SPRITE_SIZE, CUSTOM_SPRITE_SIZE))
            self.frames = []

            if not ANIMATE_SPRITE: #adding this check here allows for someone who loads an animated sprite sheet to use only the first frame from that sheet
                num_frames = 1

            #create a list of all frames in animated sprite
            for i in range(num_frames): 
                surface = pygame.Surface((CUSTOM_SPRITE_SIZE, CUSTOM_SPRITE_SIZE))
                surface.fill(BACKGROUND_COLOR)
                self.frames.append(surface)

            for i in range(len(self.frames)):
                self.frames[i].blit(self.sprite_sheet,(0,0),((i * CUSTOM_SPRITE_SIZE),0,CUSTOM_SPRITE_SIZE,CUSTOM_SPRITE_SIZE))

            #create main sprite rect and image
            self.image = pygame.Surface((CUSTOM_SPRITE_SIZE, CUSTOM_SPRITE_SIZE))
            self.image.set_colorkey(BACKGROUND_COLOR)
            self.image.blit(self.frames[0], (0,0))
            self.rect = self.image.get_rect()
            
            self.animation_frame = 0
            self.animation_frame_counter = 0
            self.animation_update_frequency = ANIMATION_SPEED #seconds
            self.animation_frames_before_switch = self.animation_update_frequency * FPS #used to count the number of frames scurry will draw before switching to the next frame in an animated sprite

            if ROTATE_SPRITE:
                self.minimum_step = 12 #determines the minimum number of pixels in any direction the mouse (cursor if sens <=1, sprite if sens >1) must move before changing the orientation of the sprite
                self.prev_deltas_list = [] #stores previous values of cursor deltas, which are summed together until the minimum step is reached. this allows for both slow mouse movements that require several steps to reach minimum step, and fast movements that do not.
                self.orientation_reference = (0,0) #stores the sums of deltas from list above in a single vector with magnitude greater than self.minimum_step
                self.rotation = 0 #stores current orientation

        else: #no custom sprite, draw a circle with user specified dimensions and colors
            self.color = CIRCLE_SPRITE_COLOR
            self.radius = CIRCLE_SPRITE_SIZE // 2
            self.image = pygame.Surface((2*self.radius, 2*self.radius))
            self.rect = self.image.get_rect()
            self.image.set_colorkey((BACKGROUND_COLOR))
            self.image.fill((BACKGROUND_COLOR))

            if  0 < CIRCLE_OUTLINE_SIZE <= CIRCLE_SPRITE_SIZE: #cannot have an outline larger than sprite itself.
                self.outline_color = CIRCLE_OUTLINE_COLOR
                self.outline_radius_thickness = (CIRCLE_OUTLINE_SIZE) / 2
                pygame.draw.circle(self.image, self.outline_color, (self.radius,self.radius), self.radius)            
                pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius - self.outline_radius_thickness)
            else:
                pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
            
            self.rotate_square_sprite_without_changing_rect(self.image,45) #to make the circle sprite look exactly like the preview in GUI. this line serves no other purpose and can be commented out if you would like.

        self.rect.centerx = round(self.float_x)
        self.rect.centery = round(self.float_y)

    def update(self, delta_x, delta_y): #called once per frame. updates sprite state and preps sprite to be drawn.
        # Update sprite position
        self.float_x += delta_x * SENSITIVITY
        self.float_y += delta_y * SENSITIVITY

        self.rect.centerx = round(self.float_x)
        self.rect.centery = round(self.float_y)

        # Handle sprite reaching edge
        if not (self.rect.right >=0 and
            self.rect.left <= APP_WINDOW_WIDTH and
            self.rect.top <= APP_WINDOW_HEIGHT and
            self.rect.bottom >= 0):

            self.wrap(wrap=WRAPPING_MODE)

        if USE_CUSTOM_SPRITE:
            if ROTATE_SPRITE: #prepare to calculate sprite orientation
                if not (delta_x == 0 and delta_y == 0): #only store non-zero deltas for orientation calculations
                    if SENSITIVITY > 1: #when calculating orientation, precision can be improved by taking the largest possible measurements. as it will require the smallest possible mouse movements to get an accurate and stable orientation calculation.
                        delta_x *= SENSITIVITY #delta_x and delta_y have served their main purpose. it is safe to modify them and re-use them.
                        delta_y *= SENSITIVITY

                    self.prev_deltas_list.insert(0,(delta_x, delta_y))
                    
                    delta_x, delta_y = 0, 0
                    updated_list = []

                    #sum deltas from the list in order of most recent until minimum step is reached. at that point the list is truncated and orientation references is updated.
                    for delta_tuple in self.prev_deltas_list:
                        delta_x += delta_tuple[0]
                        delta_y += delta_tuple[1]
                        updated_list.append((delta_tuple[0], delta_tuple[1]))

                        if math.sqrt((delta_x ** 2) + (delta_y ** 2)) > self.minimum_step:
                            break 
                    
                    self.orientation_reference = (delta_x, delta_y) #store deltas as vector
                    self.prev_deltas_list = updated_list
                    
            self.animate_sprite()
            
    def wrap(self, wrap): #function responsible for repositioning the sprite if it goes beyond the pygame display boundaries
        with wrapping_lock: #ensure that sprite properly wraps across the the screen between the time self.wrapped_last_frame is set to True and the next trail dot is created with the attribute dot.first_in_line
            self.wrapped_last_frame = True

            if not wrap: #spawn in center, otherwise wrap to opposite wall
                self.rect.center = (INITIAL_SPRITE_POSITION)
            elif self.rect.right < 0:
                self.rect.left = APP_WINDOW_WIDTH
            elif self.rect.left > APP_WINDOW_WIDTH:
                self.rect.right = 0
            if self.rect.bottom < 0:
                self.rect.top = APP_WINDOW_HEIGHT
            elif self.rect.top > APP_WINDOW_HEIGHT:
                self.rect.bottom = 0
                
            self.float_x = float(self.rect.centerx)
            self.float_y = float(self.rect.centery)

    def animate_sprite(self):
        #update sprite animation and orientation if necessary
        self.animation_frame_counter += 1

        if self.animation_frame_counter >= self.animation_frames_before_switch:
            self.animation_frame_counter = 0
            
            if self.animation_frame == len(self.frames ) - 1:
                self.animation_frame = 0
            else:
                self.animation_frame += 1


        current_image = pygame.Surface((CUSTOM_SPRITE_SIZE,CUSTOM_SPRITE_SIZE))
        current_image.blit(self.frames[self.animation_frame], (0,0))

        if ROTATE_SPRITE: #convert (delta_x, delta_y) vector into a rotation in degrees
            delta_x = self.orientation_reference[0]
            delta_y = self.orientation_reference[1]
            
            
            if delta_x == 0:
                if delta_y > 0:
                    self.rotation = -90
                else:
                    self.rotation = 90
            elif delta_y == 0:
                if delta_x > 0:
                    self.rotation = 0
                else:
                    self.rotation = 180
            else:
                self.rotation = math.atan((-1 * delta_y) / delta_x)
                self.rotation = round(self.rotation * 180 / math.pi) #convert radians to degrees and round 

                if delta_x < 0: self.rotation += 180 #compensate for range of arctan function
  
            self.rotate_square_sprite_without_changing_rect(current_image, self.rotation)

        self.image.fill(BACKGROUND_COLOR)
        self.image.blit(current_image, (0,0)) #update sprite image

    def rotate_square_sprite_without_changing_rect(self, sprite_image_surface, angle):
        original_image_width = sprite_image_surface.get_width()

        rotated_image = pygame.transform.rotate(sprite_image_surface, angle) #creates a larger rectangle!!! 
        scaling_compensation = (rotated_image.get_width() - original_image_width) / 2 #only works because sprite has a square surface
            
        sprite_image_surface.fill(BACKGROUND_COLOR)
        sprite_image_surface.blit(rotated_image,(0,0),(scaling_compensation, scaling_compensation, original_image_width, original_image_width))         

class Trail_Dot(pygame.sprite.Sprite): #the trail istelf will be comprised of separate instances of what I call "trail dots" which will spawn at a regular interval and have a finite lifetime.
    def __init__(self, x, y, velocity, first_in_line=False):
        super().__init__()
        self.init_time = time.time() #used to decide when to despawn the trail dot
        self.velocity = velocity #used to determine color of the dot
        self.color = self.get_color(self.velocity)
        self.radius = TRAIL_THICKNESS // 2
        self.first_in_line = first_in_line #used to determine where the trail should NOT be connected with line segments, i.e. when the mouse sprite is wrapped across the screen.

        self.image = pygame.surface.Surface((2 * self.radius, 2* self.radius))
        self.image.fill(BACKGROUND_COLOR)
        self.image.set_colorkey(BACKGROUND_COLOR)
        self.rect = self.image.get_rect()
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        
        self.float_x = float(x) #store position data as float for precise curve and velocity calculations
        self.float_y = float(y)

        self.rect.centerx = round(self.float_x) #round to nearest pixel when drawing to screen
        self.rect.centery = round(self.float_y)

    def update(self, current_time): #any trail dots that have been alive longer than their lifetime since last frame will be despawned
        if current_time - self.init_time > TRAIL_LIFETIME:
            self.kill()

    def get_color(self, velocity):
        #The Color of a trail dot will depend of the velocity of the mouse cursor in pixels/second. see on_move() for how velocity is calculated

        #Create a logarithmic scale for velocity        
        if velocity == 0:
            percent = 0
        else:
            percent = 10 * math.log2(velocity / 200) 
            #returns  0 if velocity is 200, 
            #returns 10 if velocity is 400, 
            #returns 20 if velocity is 800
            #returns 30 if velocity is 1600
            #returns 40 if velocity is 3200
            #returns 50 if velocity is 6400
            #returns 60 if velocity is 12800
            #returns 70 if velocity is 25600
            #returns 80 if velocity is 51200
            #returns 90 if velocity is 124000
            #returns 100 if velocity is 248000

        if percent < 0: percent = 0
        if percent > 100: percent = 100

        

        #Create parametric interpolation for 3-color linear gradient:
            #SLOW_TRAIL_COLOR | MEDIUM_FAST_TRAIL_COLOR | VERY_FAST_TRAIL_COLOR

        #Use 4 parameters:
            #MIN: 0 | SLOW_COLOR_UPPER_BOUNDARY | MEDIUM_FAST_COLOR_LOWER_BOUNDARY | MEDIUM_FAST_COLOR_UPPER_BOUNDARY | VERY_FAST_COLOR_LOWER_BOUNDARY | MAX: 100
        #Parameters must be ordered correctly between 0 and 100

        if percent < SLOW_COLOR_UPPER_BOUNDARY:
            r, g, b = SLOW_TRAIL_COLOR[0], SLOW_TRAIL_COLOR[1], SLOW_TRAIL_COLOR[2]

        elif SLOW_COLOR_UPPER_BOUNDARY <= percent <= MEDIUM_FAST_COLOR_LOWER_BOUNDARY:
            range = MEDIUM_FAST_COLOR_LOWER_BOUNDARY - SLOW_COLOR_UPPER_BOUNDARY
            position = percent - SLOW_COLOR_UPPER_BOUNDARY
            position_as_percent = position / range
            color_delta = (MEDIUM_FAST_TRAIL_COLOR[0] - SLOW_TRAIL_COLOR[0], MEDIUM_FAST_TRAIL_COLOR[1] - SLOW_TRAIL_COLOR[1], MEDIUM_FAST_TRAIL_COLOR[2] - SLOW_TRAIL_COLOR[2])
            
            r = SLOW_TRAIL_COLOR[0] + color_delta[0] * position_as_percent
            g = SLOW_TRAIL_COLOR[1] + color_delta[1] * position_as_percent
            b = SLOW_TRAIL_COLOR[2] + color_delta[2] * position_as_percent

        elif MEDIUM_FAST_COLOR_LOWER_BOUNDARY < percent < MEDIUM_FAST_COLOR_UPPER_BOUNDARY:
            r, g, b = MEDIUM_FAST_TRAIL_COLOR[0], MEDIUM_FAST_TRAIL_COLOR[1], MEDIUM_FAST_TRAIL_COLOR[2]

        elif MEDIUM_FAST_COLOR_UPPER_BOUNDARY <= percent <= VERY_FAST_COLOR_LOWER_BOUNDARY:
            range = VERY_FAST_COLOR_LOWER_BOUNDARY - MEDIUM_FAST_COLOR_UPPER_BOUNDARY
            position = percent - MEDIUM_FAST_COLOR_UPPER_BOUNDARY
            position_as_percent = position / range
            color_delta = (VERY_FAST_TRAIL_COLOR[0] - MEDIUM_FAST_TRAIL_COLOR[0], VERY_FAST_TRAIL_COLOR[1] - MEDIUM_FAST_TRAIL_COLOR[1], VERY_FAST_TRAIL_COLOR[2] - MEDIUM_FAST_TRAIL_COLOR[2])
            
            r = MEDIUM_FAST_TRAIL_COLOR[0] + color_delta[0] * position_as_percent
            g = MEDIUM_FAST_TRAIL_COLOR[1] + color_delta[1] * position_as_percent
            b = MEDIUM_FAST_TRAIL_COLOR[2] + color_delta[2] * position_as_percent

        else:
            r, g, b = VERY_FAST_TRAIL_COLOR[0], VERY_FAST_TRAIL_COLOR[1], VERY_FAST_TRAIL_COLOR[2]
       
        return (r, g, b)
        #There are probably more versatile and efficient algorithms for this, but I didn't feel like doing the research and just winged it.    

def mouse_move_status(): #Daemon thread continuously monitors in the background and determines whether or not the mouse is moving. Also used to reset sprite if cursor_idle_reset is enabled.
    #This is used to guarantee the mouse sprite stops moving when the mouse stops moving, which resolves the paradox of handling the cursor at the edge of the screen/boundary.
    global moving, moving_x, moving_y
    
    while True:
        current_time = time.time()

        # The mouse will be considered moving if it has received a position update within the past 15 milliseconds. 
        # The value of 15 milliseconds was chosen experimentally, as it seemed to provide the greatest balance between
        # having a delay that is essentially imperceptible by the end user, but not so short that it interferes with the 
        # stability of other functions in the program.
        
        with moving_lock: #use lock to ensure that no function can change the value of last_update_time while in the middle of executing this logic
            if current_time - last_update_time[0] > 0.015: #x has not moved in the past 15 milliseconds 
                moving_x = False
            else:
                moving_x = True

            if current_time - last_update_time[1] > 0.015: #y has not moved in the past 15 milliseconds
                moving_y =  False
            else:
                moving_y = True

            if ENABLE_CURSOR_IDLE_RESET:
                if current_time - max(last_update_time[0], last_update_time[1]) > CURSOR_IDLE_RESET: #if mouse has moved at all within cursor_idle_reset time:
                    mouse_sprite.wrap(wrap=False) #respawns the sprite in the center of the screen
            
        if moving_x or moving_y: #mouse has moved within the past 15 milliseconds
            moving = True
        else:
            moving = False            
        
        time.sleep(0.005) #check every 5 milliseconds

def on_move(x, y, return_delta_values=False): #tracks and stores mouse movements, creates trail effect dots, and sets value of cursor_pos tuple. Callback fucntion for mouse.listener object, but is also called by other functions.
    #explicitly put, this function is called exactly once per frame in pygame, as well as also called after every system mouse move event. when called by a function
    global cursor_pos, prev_x, prev_y, prev_velocities, buffer_x, buffer_y, moving_x, moving_y, last_update_time, prev_trail_dot, crash
    
    # at this point in the code, cursor_pos represents the previous cursor position, whereas the tuple (x,y) represents the current cursor position.
    # keep in mind that prev_x and prev_y serve different functions than cursor_pos, and so it is important that each is used respectively.
    # cursor_pos stores the previous values of x and y from the previous on_move() event. prev_x and prev_y are used as the reference points from which to measure delta values.
    # because x and y can be outside the cursor boundaries, this distinction is important. 
    # we do NOT want to use points outside of the cursor boundaries as reference points for measuring delta values.

    with moving_lock: #use lock to ensure last_update_time are updated before deciding whether the cursor is moving in mouse_move_status()
        if not cursor_pos[0] == x:
            last_update_time = (time.time(), last_update_time[1])

        if not cursor_pos[1] == y:
            last_update_time = (last_update_time[0], time.time())

    #calculate delta values from the reference points determined during the previous mouse move event
    dx = x - prev_x
    dy = y - prev_y    

    #protect against spam if cursor compltetely leaves boundaries. This workes because the pynput mouse.Controller().position attribute always returns a position within the monitor's boundaries, while the on_move method can return positions beyond the boundaries of the monitor.
    if DISABLE_MOVEMENT_IF_CURSOR_LEAVES_BOUNDARIES: 
        if not ((LOWER_X_BOUNDARY  - 1) <= cursor.position[0] <= (UPPER_X_BOUNDARY + 1) and (LOWER_Y_BOUNDARY  - 1) < cursor.position[1] <= (UPPER_Y_BOUNDARY + 1)): #provide 1 extra pixel of wiggle room beyond the boundaries to ensure program stability
            dx, dy = 0, 0

    #use a buffer to store the mouse movement data between pygame frames. the buffer will be reset when the sprite position is updated.
    buffer_x += dx
    buffer_y += dy
    
    #determine the proper reference point from which to measure delta values during the next mouse move event.
    if CENTERED_CURSOR_MODE:
        prev_x, prev_y = CENTER_SCREEN_POS[0], CENTER_SCREEN_POS[1]
    else: 
        #this very simple algorithm is the heart of the entire program. I spent way too long trying to reverse engineer this algorithm from experimental data, just to discover how simple the algorithm itself actually was. Oh well... I guess you can't be too thorough.
        if x >= UPPER_X_BOUNDARY:
            prev_x = UPPER_X_BOUNDARY - 1
        elif x <= LOWER_X_BOUNDARY:
            prev_x = LOWER_X_BOUNDARY
        else:
            prev_x = x

        if y >= UPPER_Y_BOUNDARY:
            prev_y = UPPER_Y_BOUNDARY - 1
        elif y <= LOWER_Y_BOUNDARY:
            prev_y = LOWER_Y_BOUNDARY
        else:
            prev_y = y

    cursor_pos = (x,y) #from here onwards, cursor_pos refers to the most recent mouse positon. Other functions that reference the cursor_pos variable assume it to represent the current cursor position.
    
    #spawn a trail dot if applicable
    with wrapping_lock: #use lock to ensure that mouse sprite wrapped properly after reaching screen edge when mouse_sprite.wrapped_last_frame is set to TRUE. Avoids race condition in which self.first_in_line is set before sprite is wrapped and a line is drawn across the screen. 
        current_time = time.time()
        if current_time - prev_trail_dot[2] > TRAIL_DOT_SPAWN_COOLDOWN: #control the rate at which trail dots can be spawned
            if moving: #don't waste resources on creating trail dots if not moving.
                #calculate position of new trail dot.
                trail_dot_float_x = mouse_sprite.float_x + (SENSITIVITY * buffer_x)
                trail_dot_float_y = mouse_sprite.float_y + (SENSITIVITY * buffer_y)
                
                #calculate velocity
                try:
                    if mouse_sprite.wrapped_last_frame: #do not want to count the distance moved by wrapping in velocity calculations, so we use current mouse sprite location as the location of the prev trail dot. So, in this case, dx = SENSITIVITY * buffer_x
                       prev_trail_dot = (mouse_sprite.float_x, mouse_sprite.float_y, prev_trail_dot[2])
                    
                    dx = (trail_dot_float_x - prev_trail_dot[0]) / SENSITIVITY #Divide by sensitivity to make velocity dependent on cursor movement, not sprite movement.
                    dy = (trail_dot_float_y - prev_trail_dot[1]) / SENSITIVITY
                    dt = current_time - prev_trail_dot[2] #note that the distinction here between prev_trail_dot[2], and last_update_time. last_update_time is only relevant for determining if the cursor is moving or not--it is not useful for calculating velocity. 
                    velocity = math.sqrt(dx ** 2 + dy ** 2) / dt
                except: #used just in case current_time = prev_trail_dot[2]. theoretically this should never happen, but in case it does it will be handled.
                    velocity = 0

                if VELOCITY_SMOOTHING > 0:
                    #a short algorithm for creating a moving average for velocity with VELOCITY_SMOOTHING points.
                    sum = 0
                    for v in prev_velocities:
                        sum += v

                    smoothed_velocity = (sum + velocity) / (len(prev_velocities) + 1)
                    prev_velocities.insert(0,velocity)
                    prev_velocities.pop()
                else:
                    smoothed_velocity = velocity

                #create a sort of marker or checkpoint in the list of trail dots to indicate where each curve starts and stops
                if mouse_sprite.wrapped_last_frame:
                    dot = Trail_Dot(trail_dot_float_x, trail_dot_float_y, smoothed_velocity, first_in_line=True)
                    mouse_sprite.wrapped_last_frame = False
                else:
                    dot = Trail_Dot(trail_dot_float_x, trail_dot_float_y, smoothed_velocity)
                
                trail_dot_group.add(dot)
                
                #save trail dot for velocity calculation
                prev_trail_dot = (trail_dot_float_x, trail_dot_float_y, current_time)

    if return_delta_values: #Function called by another function, and not by mouse event callback
        
        delta_x = buffer_x
        delta_y = buffer_y
        
        buffer_x = 0
        buffer_y = 0

        return(delta_x, delta_y)    
        
def update_game_state(): #calls all update functions for each frame
    global cursor_pos
    current_time = time.time()

    #get delta values. assume delta values of 0 if not moving.
    if moving: delta_x, delta_y = on_move(cursor_pos[0],cursor_pos[1], return_delta_values=True)
    if not moving_x: delta_x = 0 #necessary to eliminate edge case in which cursor sits stationary on or above upper_x_boundary and perpetually receives a false delta_x until next mouse move event.
    if not moving_y: delta_y = 0 #the solution is to only allow the sprite to move for at most 15 milliseconds before the program determines that the cursor has difinitively stopped moving. see mouse_move_status()

    
    mouse_sprite.update(delta_x, delta_y) #moves the mouse sprite to its next location
    trail_dot_group.update(current_time) #despawns any trail dots that have reached their end of lifetime

def draw_trail(): #draws the trail effect to the screen.
    counter = 0
    trail_layer = pygame.Surface((APP_WINDOW_WIDTH, APP_WINDOW_HEIGHT)) #create a new transparent surface to contstruct our trail on. idk if this intermediate step is actually necessary but it feels right to me.
    trail_layer.fill(BACKGROUND_COLOR)
    trail_layer.set_colorkey(BACKGROUND_COLOR)

    for dot in trail_dot_group: 
        # thankfully, sprite groups in pygame are ordered sequentially from first added to most recently added
        # this prevents scurry from connecting random points together with line segments, and ensures that only neighboring points are connnected
        counter += 1
        if counter == 1: #need 2 points to draw a line segment. we will use the previous dot and the current dot as our 2 points.
            prev_dot_x = round(dot.float_x)
            prev_dot_y = round(dot.float_y)
        else:
            dot_x = round(dot.float_x)
            dot_y = round(dot.float_y)

            if not dot.first_in_line: #don't connect 2 points across the screen with a line segment. separate into 2 curves.
                pygame.draw.line(trail_layer, dot.color, (dot_x, dot_y), (prev_dot_x, prev_dot_y),TRAIL_THICKNESS)

            prev_dot_x = dot_x
            prev_dot_y = dot_y
    
    screen.blit(trail_layer,(0,0)) #transfer the trail to the main pygame display.

def draw_frame(): #calls all functions required to draw each frame
    if DRAW_TRAIL_LINES: draw_trail()
    if DRAW_TRAIL_DOTS: trail_dot_group.draw(screen)
    if DRAW_MOUSE_SPRITE: mouse_sprite_group.draw(screen)

def run(config_as_dictionary=None): #main function. calls initialization function, starts and stops background threads, contains game loop and event handler, and contains clean-up code.
    initialize(config_as_dictionary) #initializes all global constants and variables. used to prevent unintended code execution should this file be imported to another file.
    #Initialize daemon threads
    mouse_moving_status = threading.Thread(target=mouse_move_status, daemon=True)
    mouse_moving_status.start()
        
    mouse_listener = mouse.Listener(on_move=on_move)
    mouse_listener.start()

    #main game loop
    sys_exit = False
    running = True
    while running: 
        #event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #user has clicked the red x to close the program. do not return to launcher
                running = False
                sys_exit = True

            if not CURRENT_PROFILE == "STANDALONE":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: #user has pressed the escape key with the app in focus. return to launcher.
                        running = False
        
        screen.fill(BACKGROUND_COLOR)
        update_game_state()
        draw_frame()

        pygame.display.flip()
        
        clock.tick(FPS)
    
    # Clean up
    mouse_listener.stop()
    time.sleep(0.1) #sleep to give the mouse_listener thread some time to to stop
    pygame.quit()

    if sys_exit:
        sys.exit()

if __name__ == "__main__":
    run()
    sys.exit()
