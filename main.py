import math
import pygame
import random

# Initialize Pygame
pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 140, 0)
BLUE = (0, 115, 255)

# Box Properties
BOX_WIDTH = 50
# Box Information List
BOX_INFO = []

BALL_RADIUS = 10
# Ball Kinetic Properties
ball_speed_x = 5 / math.sqrt(2)
ball_speed_y = 5 / math.sqrt(2)

# Threshold Distance
THRESHOLD_DISTANCE = BALL_RADIUS + BOX_WIDTH / 2

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ball Defender")

x_index_list = [i for i in range(16)]
print(x_index_list)

# Font setup
pygame.font.init()
font = pygame.font.SysFont('Arial', 24)


def create_box_with_text(box_info):
    text_surface = font.render(f"{box_info[2]}", True, box_info[3])
    text_rect = text_surface.get_rect(center=(box_info[0] + BOX_WIDTH // 2, box_info[1] + BOX_WIDTH // 2))
    screen.blit(text_surface, text_rect)


def more_balls(empty_space_indices):
    prob = random.random()
    if prob < 1 / 3:
        amount = random.randint(1, 3)
        selected_indices = random.choices(empty_space_indices, weights=None, cum_weights=None, k=amount)
        for index in selected_indices:
            this_ball_x = index * 50 + 25
            pygame.draw.circle(screen, WHITE, (ball_x, 75), 25)
            this_ball_info = [this_ball_x, 50, 1, WHITE]
            BOX_INFO.append(this_ball_info)
        return
    else:
        return


def create_new_boxes():
    number = random.randint(1, 6)
    position_index_list = x_index_list.copy()  # make an independent position_index_list

    for this_box in range(number):
        HIT_REQUIRED = math.ceil(math.sqrt(round)) * 2
        COLOR = GREEN if HIT_REQUIRED <= 5 else ORANGE if HIT_REQUIRED <= 20 else BLUE if HIT_REQUIRED <= 50 else RED
        x_position_index = random.choice(
            position_index_list)  # since the size of the index_list is constantly reduced, we need to update the upper limit too
        position_index_list.remove(x_position_index)  # in this line we update the index list
        x_pos = x_position_index * BOX_WIDTH
        y_pos = 50
        box_info = [x_pos, y_pos, HIT_REQUIRED, COLOR]
        create_box_with_text(box_info)
        BOX_INFO.append(box_info)

    more_balls(position_index_list)


def move_boxes_down():
    for this_box in BOX_INFO:
        this_box[1] += 50


def check_collision():
    def binary_search(box_list, target, key):
        low, high = 0, len(box_list) - 1
        while low <= high:
            mid = (low + high) // 2
            if key(box_list[mid]) < target:
                low = mid + 1
            elif key(box_list[mid]) > target:
                high = mid - 1
            else:
                return mid
        return -1

    for current_ball in BALL_LIST:
        ball_rect = pygame.Rect(current_ball[0] - BALL_RADIUS, current_ball[1] - BALL_RADIUS, BALL_RADIUS * 2,
                                BALL_RADIUS * 2)

        # Binary search to find the closest x coordinate
        x_index = binary_search(BOX_INFO, current_ball[0], key=lambda current_box: current_box[0])

        # Adjust the search range around the found index
        search_range = range(max(0, x_index - 2), min(len(BOX_INFO), x_index + 3)) if x_index != -1 else range(
            len(BOX_INFO))

        for i in search_range:
            this_box = BOX_INFO[i]
            brick_rect = pygame.Rect(this_box[0], this_box[1], BOX_WIDTH, BOX_WIDTH)
            if ball_rect.colliderect(brick_rect):
                if this_box[3] == WHITE:
                    BOX_INFO.remove(this_box)
                    return 1
                else:
                    ball_center = pygame.Vector2(current_ball[0], current_ball[1])
                    brick_center = pygame.Vector2(this_box[0] + BOX_WIDTH / 2, this_box[1] + BOX_WIDTH / 2)
                    collision_vector = ball_center - brick_center

                    if abs(collision_vector.x) > abs(collision_vector.y):  # Side collision
                        current_ball[2] = -current_ball[2]
                    else:  # Top/Bottom collision
                        current_ball[3] = -current_ball[3]

                    this_box[2] -= 1
                    if this_box[2] <= 0:
                        BOX_INFO.remove(this_box)
                    return 0
    return 0


def draw_arrow(surface, start, end, color, body_width=2, head_width=4, head_height=2):
    arrow = start - end
    angle = arrow.angle_to(pygame.Vector2(0, -1))
    body_length = arrow.length() - head_height
    head_verts = [
        pygame.Vector2(0, head_height / 2),
        pygame.Vector2(head_width / 2, -head_height / 2),
        pygame.Vector2(-head_width / 2, -head_height / 2),
    ]
    translation = pygame.Vector2(0, arrow.length() - (head_height / 2)).rotate(-angle)
    for i in range(len(head_verts)):
        head_verts[i].rotate_ip(-angle)
        head_verts[i] += translation
        head_verts[i] += start

    pygame.draw.polygon(surface, color, head_verts)

    if arrow.length() >= head_height:
        body_verts = [
            pygame.Vector2(-body_width / 2, body_length / 2),
            pygame.Vector2(body_width / 2, body_length / 2),
            pygame.Vector2(body_width / 2, -body_length / 2),
            pygame.Vector2(-body_width / 2, -body_length / 2),
        ]
        translation = pygame.Vector2(0, body_length / 2).rotate(-angle)
        for i in range(len(body_verts)):
            body_verts[i].rotate_ip(-angle)
            body_verts[i] += translation
            body_verts[i] += start

        pygame.draw.polygon(surface, color, body_verts)


running = True
clock = pygame.time.Clock()

screen.fill(BLACK)
round = 0
BALL_LIST = []
NUMBER_OF_BALLS = 1
mouse_clicked = False
SPEED_DEFINED = False
# FIRST_BALL_APPENDED = False
BALLS_APPENDED = False
ball_x = 100
ball_y = 590
NO_ZERO = False
MOVE = False
LAST_BALL_EXIT = False
cosine_theta = .6
sine_theta = .8

while running:
    screen.fill(BLACK)

    # Ensure BOX_INFO is sorted by x coordinate
    BOX_INFO.sort(key=lambda current_box: current_box[0])

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_clicked = True

    Mouse_x, Mouse_y = pygame.mouse.get_pos()
    mag_mouse_to_ball = math.sqrt((Mouse_x - ball_x) ** 2 + (Mouse_y - ball_y) ** 2)

    if not BOX_INFO:
        round += 1
        ball_x = random.randint(30, 770)
        ball_y = 575
        create_new_boxes()

    # if the bottom box reaches the bottom of the screen
    if BOX_INFO[0][1] + BOX_WIDTH >= SCREEN_HEIGHT:
        running = False

    # initial position of the first ball(only display the first ball before clicking)
    if not MOVE:
        pygame.draw.circle(screen, RED, (ball_x, ball_y), BALL_RADIUS)

    # redraw all boxes as the screen is updated
    for box in BOX_INFO:
        if box[3] != WHITE:
            pygame.draw.rect(screen, box[3], (box[0], box[1], BOX_WIDTH, BOX_WIDTH), width=2)
            create_box_with_text(box)
        else:
            pygame.draw.circle(screen, WHITE, (box[0], box[1] + 25), 15)

    if not mouse_clicked:
        sine_theta = ((Mouse_y - ball_y) / mag_mouse_to_ball)
        cosine_theta = ((Mouse_x - ball_x) / mag_mouse_to_ball)
        if math.asin(sine_theta) > 0:
            sine_theta = -sine_theta
        mag_pointer = 100
        dx = mag_pointer * cosine_theta
        dy = mag_pointer * sine_theta
        pointer_vector_end = pygame.Vector2(ball_x + dx, ball_y + dy)
        draw_arrow(screen, pygame.Vector2(ball_x, ball_y), pointer_vector_end, pygame.Color("green"), 10, 20, 12)

    # if the mouse is clicked and the speed of the balls is not defined

    # if the mouse is clicked, speed is defined and fixed!
    elif mouse_clicked and not SPEED_DEFINED:
        ball_speed_x = 10 * cosine_theta
        ball_speed_y = 10 * sine_theta
        SPEED_DEFINED = True
        print("Speed has been Defined!")

    # Before looping through the balls, we need to set the amount of stationary balls to zero so that it doesn't recount
    zeros = 0

    # if mouse is clicked, then all the balls will be drawn, and they will be moving
    if mouse_clicked:
        # draw all the balls, append them to the list
        if not BALLS_APPENDED:
            for n in range(NUMBER_OF_BALLS):
                ball_x -= 2 * n * ball_speed_x
                ball_y -= 2 * n * ball_speed_y
                ball_info = [ball_x, ball_y, ball_speed_x, ball_speed_y]
                BALL_LIST.append(ball_info)
            BALLS_APPENDED = True
            print(f"There are {len(BALL_LIST)} balls in the BALL_LIST")
            print(BALL_LIST)

        # The balls will be moving with the same speed defined in lines 222 and 223, collision with the edges of pages are checked
        # # # # # # MOVE
        for ball in BALL_LIST:
            ball[0] += ball[2]
            ball[1] += ball[3]
            if LAST_BALL_EXIT:
                if ball[1] >= SCREEN_HEIGHT - BALL_RADIUS:
                    ball[2] = 0
                    ball[3] = 0
                if ball[2] == 0:
                    zeros += 1
                    # print(f"Stationary ball counts: {zeros/2}")
                if ball[3] == 0:
                    zeros += 1
                # print(f"Stationary ball counts: {zeros/2}")
                if ball[0] - BALL_RADIUS <= 0 or ball[0] + BALL_RADIUS >= SCREEN_WIDTH:
                    ball[2] = -ball[2]
                if ball[1] - BALL_RADIUS <= 0:
                    ball[3] = -ball[3]
            pygame.draw.circle(screen, RED, (ball[0], ball[1]), BALL_RADIUS)
            # if the ball is at the bottom of the page, and it's still moving, set its velocities to zero
        # check the position of the last ball
        if BALL_LIST[-1][1] <= SCREEN_HEIGHT - BALL_RADIUS:
            LAST_BALL_EXIT = True

    # if all the ball are at the bottom of the screen, start a new round
    if zeros == len(BALL_LIST) * 2 and zeros != 0:
        print("new round")
        round += 1
        BALL_LIST = []
        move_boxes_down()
        create_new_boxes()
        ball_x = random.randint(0, 800)
        ball_y = 575
        mouse_clicked = False
        SPEED_DEFINED = False
        MOVE = False
        BALLS_APPENDED = False
        LAST_BALL_EXIT = False

    COLLIDE_W = check_collision()

    if COLLIDE_W == 1:
        NUMBER_OF_BALLS += 1
    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(50)

pygame.quit()
