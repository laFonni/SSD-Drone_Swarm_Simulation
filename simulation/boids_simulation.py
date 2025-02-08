from itertools import chain
from typing import List
import logging
import random


from simulation.boids.boids import BoidFlock, BoidRule, SimpleSeparationRule, AvoidWallsRule, AlignmentRule, \
    CohesionRule, \
    AvoidObstaclesRule, NoiseRule, AttractionRule, SideBySideFormationRule, AntiCollisionRule
from simulation.config.game_settings import GameSettings
from simulation.obstacles.obstacle import *
import sys

from simulation.map.map import Map
from simulation.map.human import Human


logging.basicConfig()
logger = logging.getLogger(__name__)


pygame.init()

def parameter_selection_screen():
    if not pygame.font.get_init():
        pygame.font.init()

    pygame.display.set_caption("Parameter Selection - Boid Simulation")
    screen = pygame.display.set_mode((1024, 768))
    font = pygame.font.Font(None, 36)
    title_font = pygame.font.Font(None, 48)
    clock = pygame.time.Clock()

    # Default parameter values
    parameters = {
        "n_boids": 30,
        "n_humans": 15,
        "boid_fear": 20,
        "boid_radius": 50,
        "boid_max_speed": 100,
        "simulation_time": 40,
        "rows" : 0,
        "columns" : 0
    }

    input_boxes = {
        key: pygame.Rect(400, 120 + i * 60, 200, 40)
        for i, key in enumerate(parameters.keys())
    }
    active_box = None
    user_inputs = {key: str(value) for key, value in parameters.items()}

    def draw_button(rect, text, color, text_color):
        pygame.draw.rect(screen, color, rect, border_radius=10)
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

    def draw_screen():
        screen.fill((30, 30, 30))
        title = title_font.render("Parameter Selection", True, (255, 255, 255))
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 30))

        label_x = screen.get_width() // 2 - 200
        box_x = screen.get_width() // 2 + 50

        for i, (key, rect) in enumerate(input_boxes.items()):
            label = font.render(f"{key.replace('_', ' ').capitalize()}: ", True, (200, 200, 200))
            screen.blit(label, (label_x, rect.y + 5))

            rect.x = box_x

            if key == active_box:
                pygame.draw.rect(screen, (0, 100, 0), rect, border_radius=5)
            else:
                pygame.draw.rect(screen, (100, 100, 100), rect, border_radius=5)

            pygame.draw.rect(screen, (200, 200, 200), rect, 2, border_radius=5)
            text_surface = font.render(user_inputs[key], True, (255, 255, 255))
            screen.blit(text_surface, (rect.x + 10, rect.y + 5))

        button_width = 150
        button_height = 50
        spacing = 50
        total_width = 2 * button_width + spacing

        start_button = pygame.Rect(screen.get_width() // 2 - total_width // 2, 700, button_width, button_height)
        reset_button = pygame.Rect(screen.get_width() // 2 - total_width // 2 + button_width + spacing, 700,
                                   button_width, button_height)

        draw_button(start_button, "Start", (0, 200, 0), (0, 0, 0))
        draw_button(reset_button, "Reset", (200, 0, 0), (255, 255, 255))

        return start_button, reset_button

    while True:
        start_button, reset_button = draw_screen()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Activate the clicked input box
                for key, rect in input_boxes.items():
                    if rect.collidepoint(event.pos):
                        active_box = key
                        break
                else:
                    active_box = None

                # Check if buttons were clicked
                if start_button.collidepoint(event.pos):
                    # Return parsed parameters
                    try:
                        return {key: int(value) for key, value in user_inputs.items()}
                    except ValueError:
                        print("Invalid input: Ensure all values are integers.")
                        continue
                if reset_button.collidepoint(event.pos):
                    # Reset to default values
                    user_inputs = {key: str(value) for key, value in parameters.items()}

            if event.type == pygame.KEYDOWN and active_box:
                # Edit the active input box
                if event.key == pygame.K_BACKSPACE:
                    user_inputs[active_box] = user_inputs[active_box][:-1]
                elif event.unicode.isdigit():
                    user_inputs[active_box] += event.unicode

        clock.tick(30)


def show_results_screen(humans_found):
    if not pygame.font.get_init():
        pygame.font.init()
    pygame.display.set_caption("Simulation Results")
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()

    restart_button = pygame.Rect(300, 400, 200, 50)  # Define the Restart button rectangle

    running = True
    while running:
        screen.fill((30, 30, 30))
        text = font.render(f"Humans found: {humans_found}", True, (255, 255, 255))
        screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, screen.get_height() // 2 - 100))

        # Draw the Restart button
        pygame.draw.rect(screen, (0, 200, 0), restart_button, border_radius=10)
        restart_text = small_font.render("Restart", True, (0, 0, 0))
        screen.blit(restart_text, (restart_button.x + (restart_button.width - restart_text.get_width()) // 2,
                                   restart_button.y + (restart_button.height - restart_text.get_height()) // 2))

        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.collidepoint(event.pos):
                    running = False
                    #parameter_selection_screen()

    pygame.quit()


def check_collision(entity1, entity2, radius):
    entity2_x, entity2_y = entity2.pos
    distance = ((entity1.x - entity2_x) ** 2 + (entity1.y - entity2_y) ** 2) ** 0.5
    return distance < radius

def is_valid_position(x, y, obstacles):
    for obstacle in obstacles:
        if obstacle.contains((x, y)):
            return False
    return True

def main():
    while True:

        parameters = parameter_selection_screen()

        # Extract parameters
        n_boids = parameters["n_boids"]
        n_humans = parameters["n_humans"]
        boid_fear = parameters["boid_fear"]
        boid_radius = parameters["boid_radius"]
        boid_max_speed = parameters["boid_max_speed"]
        simulation_time = parameters["simulation_time"]
        rows = parameters["rows"]
        columns = parameters["columns"]

        game_settings = GameSettings()
        # game_settings.debug = True

        pygame.display.set_caption("Boid Simulation")
        win = pygame.display.set_mode((game_settings.window_width, game_settings.window_height))
        fill_colour = (204,204,204)
        light_gray = (200, 200, 200)

        human_positions = [(random.randint(0, win.get_width()), random.randint(0, win.get_height())) for _ in range(n_humans)]
        humans = [Human(x, y) for x, y in human_positions]

        max_width = win.get_width()
        max_height = win.get_height()

        sim_map = Map(max_width, max_height, rows, columns)

        rect1 = RectangleObstacle(random.randint(0, max_width), random.randint(0, max_height), 300, 100, light_gray)
        rect2 = RectangleObstacle(random.randint(0, max_width), random.randint(0, max_height), 100, 300, light_gray)
        circ1 = CircleObstacle(random.randint(0, max_width), random.randint(0, max_height), 100, light_gray)
        circ2 = CircleObstacle(random.randint(0, max_width), random.randint(0, max_height), 120, light_gray)

        polygon1_vertices = [(0, 0), (150, 50), (100, 100), (-50, 50)]
        polygon2_vertices = [(0, 0), (100, 50), (50, 100), (-50, 50)]
        polygon3_vertices = [(0, 0), (200, 100), (150, 200), (-100, 100)]
        polygon4_vertices = [(0, 0), (250, 150), (200, 300), (-150, 150)]

        polyg1_origin = (random.randint(0, max_width), random.randint(0, max_height))
        polyg2_origin = (random.randint(0, max_width), random.randint(0, max_height))
        polyg3_origin = (random.randint(0, max_width), random.randint(0, max_height))
        polyg4_origin = (random.randint(0, max_width), random.randint(0, max_height))

        polyg1 = PolygonObstacle([(x + polyg1_origin[0], y + polyg1_origin[1]) for x, y in polygon1_vertices], light_gray)
        polyg2 = PolygonObstacle([(x + polyg2_origin[0], y + polyg2_origin[1]) for x, y in polygon2_vertices], light_gray)
        polyg3 = PolygonObstacle([(x + polyg3_origin[0], y + polyg3_origin[1]) for x, y in polygon3_vertices], light_gray)
        polyg4 = PolygonObstacle([(x + polyg4_origin[0], y + polyg4_origin[1]) for x, y in polygon4_vertices], light_gray)


        def generate_circle_obstacles(map_width, map_height, num_obstacles, min_radius, max_radius, color):
            obstacles = []
            for _ in range(num_obstacles):
                x = random.randint(0, map_width)
                y = random.randint(0, map_height)
                radius = random.randint(min_radius, max_radius)
                obstacles.append(CircleObstacle(x, y, radius, color))
            return obstacles

        obstacles = generate_circle_obstacles(
            game_settings.map_width, game_settings.map_height, num_obstacles=70, min_radius=10, max_radius=20, color=(119, 49, 9)
        )

        

        human_positions = []
        for _ in range(n_humans):
            while True:
                x, y = random.randint(0, win.get_width()), random.randint(0, win.get_height())
                if is_valid_position(x, y, obstacles):
                    human_positions.append((x, y))
                    break

        humans = [Human(x, y) for x, y in human_positions]

        flock = BoidFlock(game_settings)
        flock_rules: List[BoidRule] = [
            # CohesionRule(weighting=0.1, game_settings=game_settings),
            AlignmentRule(weighting=0.9, game_settings=game_settings),
            SimpleSeparationRule(weighting=0.4, game_settings=game_settings, push_force=boid_fear),
            AvoidWallsRule(weighting=1.5, game_settings=game_settings, push_force=100),
            # SideBySideFormationRule(weighting=0.3, game_settings=game_settings, spacing=50, noise_factor=0.1),
            AvoidObstaclesRule(weighting=1.5, game_settings=game_settings, obstacles=obstacles, push_force=100),
            NoiseRule(weighting=0.2, game_settings=game_settings),
            # AntiCollisionRule(weighting=0.7, game_settings=game_settings)
            # AttractionRule(weighting=1, game_settings=game_settings, sim_map=sim_map)
        ]

        def generate_positions_in_sector(n_boids, win, obstacles):
            """Generuje pozycje dla dronów w losowo wybranym sektorze planszy."""
            positions = []

            width, height = win.get_width(), win.get_height()
            sector_width, sector_height = width // 3, height // 3
            sector_x_start = random.choice([0, width // 3])
            sector_y_start = random.choice([0, height // 3])
            sector_x_end = sector_x_start + sector_width
            sector_y_end = sector_y_start + sector_height

            for _ in range(n_boids):
                while True:
                    x = random.randint(sector_x_start, sector_x_end - 1)
                    y = random.randint(sector_y_start, sector_y_end - 1)

                    if is_valid_position(x, y, obstacles) and not any(
                            ((x - px) ** 2 + (y - py) ** 2) ** 0.5 < 15 for px, py in positions
                    ):
                        positions.append((x, y))
                        break

            return positions

        positions = generate_positions_in_sector(n_boids, win, obstacles)

        flock.generate_boids(n_boids, positions, rules=flock_rules, local_radius=boid_radius, max_velocity=boid_max_speed)
        # flock.generate_boids(n_boids, rules=flock_rules, local_radius=boid_radius, max_velocity=boid_max_speed)
        
        entities = flock.boids
        tick_length = int(1000/game_settings.ticks_per_second)


        last_tick = pygame.time.get_ticks()
        simulation_start_time = pygame.time.get_ticks()
        humans_found = 0

        i = 0
        while game_settings.is_running:
            win.fill(fill_colour)

            # print(list(sim_map.sectors))
            for sector in list(chain(*sim_map.sectors)):

                for boid in entities:
                    if sector.contains_point(boid.pos):
                        sector.mark_searched()

            time_since_last_tick = pygame.time.get_ticks() - last_tick
            sim_map.draw(win)

            # if (pygame.time.get_ticks() - simulation_start_time) > (simulation_time * 1000) / 4 * 3:
            #     sim_map.update_attractiveness()

            for obstacle in obstacles:
                obstacle.draw(win)

            humans = [human for human in humans if not any(check_collision(human, boid, 20) for boid in entities)]
            humans_found = n_humans - len(humans)

            for i in range(len(humans)):
                Human.draw(humans[i], win)




            if time_since_last_tick < tick_length:
                pygame.time.delay(tick_length - time_since_last_tick)

            time_since_last_tick = pygame.time.get_ticks() - last_tick

            last_tick = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_settings.is_running = False

            keys = pygame.key.get_pressed()

            if (pygame.time.get_ticks() - simulation_start_time) > simulation_time * 1000:
                break

            for entity in entities:
                entity.update(keys, win, time_since_last_tick/1000)

            pygame.display.flip()
        show_results_screen(f'{humans_found} out of {n_humans} humans found')
        pygame.quit()


if __name__ == '__main__':
    main()
