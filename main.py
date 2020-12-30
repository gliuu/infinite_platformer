import pygame, sys, os, random

clock = pygame.time.Clock()

from pygame.locals import *
pygame.mixer.pre_init(44100,-16,2,512)
pygame.init()
pygame.mixer.set_num_channels(64)

pygame.display.set_caption("My Pygame Window")

WINDOW_SIZE = (800, 400)

screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
display = pygame.Surface((400,200))

font = pygame.font.SysFont(None,24)
slow_death_img = font.render("Too slow; you died", True, (0,0,0))
fall_death_img = font.render("You fell to your death", True, (0,0,0))
#hit_death_img = font.render("You bonked your head too much", True, (0,0,0))
#fast_death_img = font.render("Victoria Liu found this bug. You died", True, (0,0,0))

moving_right = False
moving_left = False
vertical_momentum = 0
air_timer = 0
life_counter = 100

#grass_sound_timer = 0
CHUNK_SIZE = 8

true_scroll = [0,0]
def generate_chunk(x,y):
    chunk_data = []
    for y_pos in range(CHUNK_SIZE):
        for x_pos in range(CHUNK_SIZE):
            target_x = x * CHUNK_SIZE + x_pos
            target_y = y * CHUNK_SIZE + y_pos
            tile_type = 0
            if target_y == 3:
                if random.randint(1,5) == 1:
                    tile_type = 2
            elif target_y == 10:
                if random.randint(1,2) == 1:
                    tile_type = 1
            elif target_y == 9:
                if random.randint(1, 2) == 1:
                    tile_type = 1
            elif target_y == 8:
                if random.randint(1,3) == 1:
                    tile_type = 1
            elif target_y == 5:
                if random.randint(1,10) == 1:
                    tile_type = 1
            #elif target_y == 6
                #if random.randint(1,3) == 1:
                    #tile_type = 1
            #elif target_y == 7:
                #if random.randint(1, 6) == 1:
                    #tile_type = 1
            if tile_type != 0:
                chunk_data.append([[target_x,target_y],tile_type])
    return chunk_data

def load_map(path):
    f = open(path + '.txt')
    data = f.read()
    f.close()
    data = data.split('\n')
    game_map = []
    for row in data:
        game_map.append(list(row))
    return game_map

global animation_frames
animation_frames = {}

def load_animation(path,frame_durations):
    global animation_frames
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n=0
    for frame in frame_durations:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id + '.png'
        animation_image = pygame.image.load(img_loc)
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data

def change_action(action_var,frame,new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var,frame


animation_database = {}
animation_database['moving'] = load_animation('player_animations/moving',[120,20])
animation_database['idle'] = load_animation('player_animations/idle',[120,20])
animation_database['death'] = load_animation('player_animations/death',[30])

player_action = 'idle'
player_frame = 0
player_flip = False

jump_sound = pygame.mixer.Sound('jump1.wav')
#grass_sounds = [pygame.mixer.Sound('grass_0.wav'),pygame.mixer.Sound('grass_1.wav')]
#grass_sounds[0].set_volume(0.2)
#grass_sounds[1].set_volume(0.2)
#pygame.mixer.music.load('BoB.mp3')
#pygame.mixer.music.play(-1)

game_map = {}
grass_image = pygame.image.load('grass_image.png')
dirt_image = pygame.image.load('dirt_image.png')
trunk_image = pygame.image.load('trunk_image.png').convert()
trunk_image.set_colorkey((255,255,255))
leaves_image = pygame.image.load('leaves_image.png').convert()
leaves_image.set_colorkey((255,255,255))

tile_index = {1:dirt_image,
              2:grass_image,
              4:leaves_image}

#player_image = pygame.image.load('players.png')

player_rect = pygame.Rect(100,100,20,30)

background_objects = [[0.25,[150,10,70,400]],[0.25,[100,30,40,400]],[0.5,[30,40,40,400]],[0.5,[130,90,100,400]],[.5,[300,80,120,400]]]

def collision_test(rect,tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list

def move(rect,movement,tiles):
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    rect.x += movement[0]
    hit_list = collision_test(rect,tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += movement[1]
    hit_list = collision_test(rect,tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect, collision_types




while True:
    display.fill((40, 142, 219))

    #scroll[0] += player_rect.x
    #print(scroll[0])
    #print(player_rect.x)

    #scroll[0] += (player_rect.x-scroll[0]-123)
    #scroll[1] += (player_rect.y-scroll[1]-123)
    #true_scroll[0] += (player_rect.x-true_scroll[0]-90)
    true_scroll[1] += (player_rect.y-true_scroll[1]-110)
    true_scroll[0] += 1
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])

    #if grass_sound_timer > 0:
        #grass_sound_timer -= 1

    pygame.draw.rect(display,(255,179,217),pygame.Rect(0,120,300,300))
    #pygame.draw.rect(display,(80,10,10),pygame.Rect(0,120,300,300))
    for background_object in background_objects:
        obj_rect = pygame.Rect(background_object[1][0]-scroll[0]*background_object[0],background_object[1][1]-scroll[1]*background_object[0],background_object[1][2],background_object[1][3])
        if background_object[0] == 0.5:
            pygame.draw.rect(display,(14,222,150),obj_rect)
        if background_object[0] == 0.25:
            pygame.draw.rect(display,(120,15,50),obj_rect)
    tile_rects = []
    for y in range(3):
        for x in range(4):
            target_x = x - 1 + int(round(scroll[0]/(CHUNK_SIZE*20)))
            target_y = y - 1 + int(scroll[1]/(CHUNK_SIZE*20))
            target_chunk = str(target_x)  + ';' + str(target_y)
            if target_chunk not in game_map:
                game_map[target_chunk] = generate_chunk(target_x,target_y)
            for tile in game_map[target_chunk]:
                #display.blit(tile_index[tile[1]],(tile[0][0]*20-scroll[0],tile[0],[1]*20-scroll[1]))
                display.blit(tile_index[tile[1]], (tile[0][0] * 20 - scroll[0], tile[0][1] * 20 - scroll[1]))
                if tile[1] in [1,2,4]:
                    tile_rects.append(pygame.Rect(tile[0][0]*20,tile[0][1]*20,20,20))
    #for layer in game_map:
        #x = 0
        #x = 0
    #    for tile in layer:
    #       if tile == '1':
     #           display.blit(dirt_image,(x*20,y*20))
      #      if tile == '2':
       #         display.blit(grass_image,(x*20,y*20))
        #    if tile == '3':
         #       display.blit(trunk_image,(x*20,y*20))
          #  if tile == '4':
           #     display.blit(leaves_image,(x*20,y*20))
            #if tile != '0':
             #   tile_rects.append(pygame.Rect(x*20,y*20,20,20))
            #x += 1
        #y += 1

            #if tile != '0':
                #tile_rects.append(pygame.Rect(x*20-scroll[0],y*20-scroll[1],20,20))

    player_movement = [0,0]
    if moving_right == True:
        player_movement[0] += 2
    if moving_left == True:
        player_movement[0] -= 2
    player_movement[1] += vertical_momentum
    vertical_momentum += 0.2
    if vertical_momentum > 3:
        vertical_momentum = 3
#    print(scroll[0], scroll[1])

    if player_movement[0] > 0:
        player_flip = False
        player_action,player_frame = change_action(player_action,player_frame,'moving')
    if player_movement[0] < 0:
        player_flip = True
        player_action,player_frame = change_action(player_action,player_frame,'moving')
    if player_movement[0] == 0:
        player_action,player_frame = change_action(player_action,player_frame,'idle')

    player_rect,collisions = move(player_rect,player_movement,tile_rects)
    #if collisions['bottom'] != True:
        #player_action, player_frame = change_action(player_action, player_frame, 'moving')
    if air_timer > 6:
        player_action, player_frame = change_action(player_action, player_frame, 'moving')
    if player_rect.y > 600:
        player_action, player_frame = change_action(player_action, player_frame, 'death')
        display.blit(fall_death_img, (20,20))
    if player_rect.y > 800:
        pygame.quit()
        sys.exit()



    if collisions['bottom'] == True:
        air_timer = 0
        vertical_momentum = 0
        #if player_movement[0] != 0:
            #grass_sound_timer = 30
            #random.choice(grass_sounds).play()
    else:
        air_timer += 1
    #if collisions['top'] == True:
        #life_counter -= 1
    #if life_counter < 0:
        #player_action,player_frame = change_action(player_action,player_frame,'death')
        #display.blit(hit_death_img, (20, 20))
    if player_rect.x + 30 < scroll[0]:
        display.blit(slow_death_img, (20, 20))

    if player_rect.x + 30 < scroll[0] - 100:
        pygame.quit()
        sys.exit()
    if player_rect.x > scroll[0] + 500:
        #display.blit(fast_death_img, (20, 20))
        pygame.quit()
        sys.exit()

    player_frame += 1
    if player_frame >= len(animation_database[player_action]):
        player_frame = 0
    player_img_id = animation_database[player_action][player_frame]
    player_img = animation_frames[player_img_id]
    display.blit(player_img, (player_rect.x-scroll[0], player_rect.y-scroll[1]))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_m:
                pygame.mixer.music.fadeout(1000)
            if event.key == K_n:
                pygame.mixer.music.play(-1)
            if event.key == K_RIGHT:
                moving_right = True
            if event.key == K_LEFT:
                moving_left = True
            if event.key == K_UP:
                if air_timer < 6:
                    jump_sound.play()
                    vertical_momentum = -7
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                moving_right = False
            if event.key == K_LEFT:
                moving_left = False


    screen.blit(pygame.transform.scale(display,WINDOW_SIZE),(0,0))
    pygame.display.update()
    clock.tick(60)