import arcade
import math
import random

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Pirate Plunder"
CHARACTER_SCALING = .5
TILE_SCALING = 0.5
BULLET_SPEED = 10
MUSIC_LIST = [r'Sounds\You Are a Pirate.mp3', r'Sounds\ALESTORM - Drink (8 bit Remix).mp3', r'Sounds\Alestorm-Captain Morgan Revenge (8-bit).mp3']
# How fast to move, and how fast to run the animation
PLAYER_MOVEMENT_SPEED = 10
UPDATES_PER_FRAME = 5

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]

class MyGame(arcade.View):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__()
        self.player_list = None
        self.player_sprite = None
        self.physics_engine = None
        self.wall_list = None
        self.decor_list = None
        self.ground_list = None
        self.game_over = False
        self.enemy_list = None
        self.enemy_sprite = None
        self.bgm = music(MUSIC_LIST[1])
        self.invince_timer = 0
        self.bullet_list = None
        self.num_enemies = 3
        self.Wave = 0
        self.wave_transition = True
        self.tranistion_counter = 0
        self.gunshot_sound = None

        arcade.set_background_color(arcade.csscolor.BLUE_VIOLET)

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.decor_list = arcade.SpriteList()
        self.ground_list = arcade.SpriteList()
        self.score = 0
        '''self.gunshot_sound = music("Sounds\gun_1911.mp3")'''
        
        # Set up the player, specifically placing it at these coordinates.
        image_source = 'Images\pirate.png'

        self.player_sprite = Player(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128
        self.player_list.append(self.player_sprite)

         # --- Load in a map from the tiled editor ---

        # Name of map file to load
        map_name = "map\PirateMap.tmx"

        # Read in the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)

        # -- Platforms
        water = arcade.tilemap.process_layer(map_object=my_map,
                                                    layer_name='Water',
                                                    scaling=TILE_SCALING,
                                                    base_directory = '\map',
                                                    use_spatial_hash=True,
                                                    hit_box_algorithm='Simple')
        trees = arcade.tilemap.process_layer(map_object=my_map,
                                                    layer_name='TREES',
                                                    scaling=TILE_SCALING,
                                                    base_directory = '\map',
                                                    use_spatial_hash=True,
                                                    hit_box_algorithm='Simple')
        self.wall_list.append(water)
        self.wall_list.append(trees)

        # -- decor
        self.decor_list = arcade.tilemap.process_layer(my_map, 'Decor', TILE_SCALING)

        self.ground_list = arcade.tilemap.process_layer(my_map, 'Ground', TILE_SCALING)

        #Floor
        #for x in range(0, 1250, 32): 
           # wall = arcade.Sprite("Images\wall.png", TILE_SCALING)
           # wall.center_x = x
          #  wall.center_y = 15
           # self.wall_list.append(wall)
        
        #Ceiling
        #for x in range(0, 1250, 32):
           # wall = arcade.Sprite("Images\wall.png", TILE_SCALING)
           # wall.center_x = x
           # wall.center_y = 635
           # self.wall_list.append(wall)

        #for y in range(0, 1250, 32):
           # wall = arcade.Sprite("Images\wall.png", TILE_SCALING)
           # wall.center_x = 15
           # wall.center_y = y
           # self.wall_list.append(wall)
            
        #for y in range(0, 1250, 32):
           # wall = arcade.Sprite("Images\wall.png", TILE_SCALING)
          #  wall.center_x = 985
           # wall.center_y = y
           # self.wall_list.append(wall)

        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.wall_list)

    def on_draw(self):
        """ Render the screen. """

        arcade.start_render()
        self.player_list.draw()
        self.ground_list.draw()
        self.wall_list.draw()
        self.decor_list.draw()
        self.enemy_list.draw()
        self.bullet_list.draw()

        # Put the health on the screen.
        output = f"Health: {self.player_sprite.player_health}"
        arcade.draw_text(output, 10, 630, arcade.color.WHITE, 14)

        # Put the score on the screen.
        output = f"Score: {self.score}"
        arcade.draw_text(output, 10, 10, arcade.color.WHITE, 14)
        if self.wave_transition:
            waveMsg = f"Wave {self.Wave}"
            arcade.draw_text(waveMsg, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, arcade.color.BLACK, 
                        font_size=75, anchor_x="center")

    def on_mouse_press(self, x, y, button, modifiers):
        """ Called whenever the mouse button is clicked. """

        # Create a bullet
        bullet = arcade.Sprite(r"Images\better_bullet.png", .2)

        # Position the bullet at the player's current location
        start_x = self.player_sprite.center_x
        start_y = self.player_sprite.center_y
        bullet.center_x = start_x
        bullet.center_y = start_y

        # Get from the mouse the destination location for the bullet
        # IMPORTANT! If you have a scrolling screen, you will also need
        # to add in self.view_bottom and self.view_left.
        dest_x = x
        dest_y = y

        # Do math to calculate how to get the bullet to the destination.
        # Calculation the angle in radians between the start points
        # and end points. This is the angle the bullet will travel.
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)

        # Angle the bullet sprite so it doesn't look like it is flying
        # sideways.
        bullet.angle = math.degrees(angle)
        print(f"Bullet angle: {bullet.angle:.2f}")

        # Taking into account the angle, calculate our change_x
        # and change_y. Velocity is how fast the bullet travels.
        bullet.change_x = math.cos(angle) * BULLET_SPEED
        bullet.change_y = math.sin(angle) * BULLET_SPEED

        # Add the bullet to the appropriate lists
        self.bullet_list.append(bullet)
        '''self.gunshot_sound.play(.3)'''

    def on_update(self, delta_time):
        """ Movement and game logic """
        if self.bgm.get_stream_position() == 0:
            self.bgm.play()

        # Move the player with the physics engine
        if not self.game_over:
            self.physics_engine.update()
            for enemy in self.enemy_list:
                enemy.chase_player(self.player_sprite)
            self.bullet_list.update()

        self.player_list.update_animation()

        for enemy in self.enemy_list:
            enemy.update_animation()
        PlayerCollide = arcade.check_for_collision_with_list(self.player_sprite, self.enemy_list)
        
        for collide in PlayerCollide:
            if not self.player_sprite.is_invincible:
                self.player_sprite.lose_health(1)
                self.player_sprite.is_invincible = True
        
        if self.player_sprite.is_invincible == True:
            self.invince_timer += delta_time
            
        if self.invince_timer > 3:
            self.player_sprite.is_invincible = False
            self.invince_timer = 0
            
        if self.player_sprite.player_health == 0:
            self.bgm.stop()
            end = gameOver()
            self.window.show_view(end)

        for bullet in self.bullet_list:
            hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)
            wall_hit_list = arcade.check_for_collision_with_list(bullet, self.wall_list)

            # If it did, get rid of the bullet
            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()
            
            for enemy in hit_list:
                enemy.remove_from_sprite_lists()
                self.score += 1

            if len(wall_hit_list) > 0:
                bullet.remove_from_sprite_lists()

        if len(self.enemy_list) == 0:
            self.wave_transition = True

        if self.wave_transition == True:
            if self.tranistion_counter == 0:
                self.Wave += 1
            if self.tranistion_counter < 3:
                self.tranistion_counter += delta_time
            else: 
                self.wave_transition = False
                self.tranistion_counter = 0
                if self.Wave % 3 == 0:
                    self.num_enemies += 2
                for i in range(self.num_enemies):
                    success_spawn = False
                    enemy_sprite = Enemy('Images\enemy.png', CHARACTER_SCALING,1, 3)
                    while not success_spawn:
                        enemy_sprite.center_x = random.randrange(SCREEN_WIDTH)
                        enemy_sprite.center_y = random.randrange(SCREEN_HEIGHT)

                        # See if the coin is hitting a wall
                        wall_hit_list = arcade.check_for_collision_with_list(enemy_sprite, self.wall_list)

                        player_hit_list = arcade.check_for_collision_with_list(enemy_sprite, self.player_list)

                        if len(wall_hit_list) == 0 and len(player_hit_list) == 0:
                            # It is!
                            success_spawn = True

                    self.enemy_list.append(enemy_sprite)

    def on_key_press(self, key, modifiers):
        """Cend = gameOver()
            self.Window.show_view(end)whenever a key is pressed. """

        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
    
    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """ 

        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.change_y = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0

class splashScreen(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.color.WHITE)
        self.background = arcade.load_texture('Images\THE_MATTMAN.png')
        self.counter = 0

    def on_draw(self):
        arcade.start_render()
        arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50, self.background, 2)

    def on_update(self, dt):
        self.counter += dt
        if self.counter > 5:
            menu = mainMenu()
            self.window.show_view(menu)

class mainMenu(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.color.ANTIQUE_RUBY)
        self.bgm = music(MUSIC_LIST[0])
        self.background = arcade.load_texture('Images\pirate.png')
        
    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Pirate Plunder", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, arcade.color.BLACK, 
                        font_size=75, anchor_x="center")
        arcade.draw_text("CLICK TO START", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 -50, arcade.color.BLACK, 
                        font_size=40, anchor_x="center")
        arcade.draw_scaled_texture_rectangle(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 200, self.background, 2)
    
    def on_mouse_press(self,_x,_y,_button,_modifiers):
        self.bgm.stop()
        game = MyGame()
        game.setup()
        self.window.show_view(game)

class gameOver(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.color.ANTIQUE_RUBY)
        self.bgm = music(MUSIC_LIST[2])
        
    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Game Over", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, arcade.color.BLACK, 
                        font_size=75, anchor_x="center")
        arcade.draw_xywh_rectangle_filled(SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT/2 - 50,200,50,arcade.color.BLACK)
        arcade.draw_text("RESTART", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50, arcade.color.WHITE, 
                        font_size=40, anchor_x="center")
    
    def on_mouse_press(self,_x,_y,_button,_modifiers):
        if _x < SCREEN_WIDTH/2 + 100 and _x > SCREEN_WIDTH/2 - 100 and _y < SCREEN_HEIGHT/2 and _y > SCREEN_HEIGHT/2 - 50:
            self.bgm.stop()
            menu = mainMenu()
            self.window.show_view(menu)

class music(arcade.Sound):
    '''Plays the music'''
    def __init__(self, filename):
        super().__init__(filename)
        self.play(.3)

class Player(arcade.Sprite):
    ''''''
    def __init__(self, filename, scale):
        super().__init__()
        self.character_face_direction = RIGHT_FACING
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING
        self.points = [[-32, -32], [32, -32], [32, 32], [-32, 32]]
        self.idle_texture_pair = load_texture_pair(f"Images\pirate.png")
        self.player_health = 3
        self.is_invincible = False

    def lose_health(self, damage_taken):
        self.damage_taken = damage_taken
        self.player_health -= self.damage_taken
    
    def update_animation(self, delta_time: float = 1/60):

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING
        
        self.texture = self.idle_texture_pair[self.character_face_direction]

class Enemy(arcade.Sprite):
    def __init__(self, filename, scale, enemy_damage, mv_speed):
        super().__init__(filename, scale)
        '''self.character_face_direction = RIGHT_FACING
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING
        self.points = [[-32, -32], [32, -32], [32, 32], [-32, 32]]
        self.enemy_textures = []'''

        '''for i in range(4):
            self.enemy_textures.append(arcade.load_texture("\Images\Walk.png",x = i * 150, y = 0, width= 150, height=150))'''

        self.enemy_damage = enemy_damage
        self.mv_speed = mv_speed

    def chase_player(self, player_sprite):
        """ Allows the enemy to chase the player. """
        if self.center_y < player_sprite.center_y:
            self.center_y += min(self.mv_speed, player_sprite.center_y - self.center_y)
        elif self.center_y > player_sprite.center_y:
            self.center_y -= min(self.mv_speed, self.center_y - player_sprite.center_y)

        if self.center_x < player_sprite.center_x:
            self.center_x += min(self.mv_speed, player_sprite.center_x - self.center_x)
        elif self.center_x > player_sprite.center_x:
            self.center_x -= min(self.mv_speed, self.center_x - player_sprite.center_x)
    
    '''def update_animation(self, delta_time: float = 1/60):
        # Figure out if we need to flip face left or right

        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING
        
        self.cur_texture += 1
        if self.cur_texture > 4 * UPDATES_PER_FRAME:
            self.cur_texture = 0
        frame = self.cur_texture // UPDATES_PER_FRAME
        direction = self.character_face_direction
        self.texture = self.enemy_textures[self.cur_texture]'''


def main():
    """ Main method """
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    menu = splashScreen()
    window.show_view(menu)
    arcade.run()

if __name__ == "__main__":
    main()