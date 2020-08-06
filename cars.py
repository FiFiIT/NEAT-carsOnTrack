import pygame
import neat
import time
import os
import math
from itertools import product
pygame.font.init()

# load images
BG_IMG = pygame.image.load(os.path.join("imgs", "track.png"))
CARS = pygame.image.load(os.path.join("imgs", "cars.png"))

WIN_WIDTH = BG_IMG.get_width()
WIN_HEIGHT = BG_IMG.get_height()
RADIUS_LENGTH = 190

STAT_FONT = pygame.font.SysFont('comicsans', 40)

DEBUG = True


class Car:
    def __init__(self, carsIMG, i=0, gates=[]):
        # self.offset_x1 = 2
        # self.offset_y1 = 20
        # self.offset_x2 = 4
        # self.offset_y2 = 20
        # self.car_widht = 58
        # self.car_height = 82

        # self.rect = pygame.Rect(self.offset_x1 + self.car_number * (self.offset_x2 + self.car_widht),
        #                         self.offset_y1 + self.cars_row*(self.offset_y2 + self.car_height), self.car_widht, self.car_height)
        self.offset_x1 = 20
        self.offset_x2 = 23
        self.offset_y1 = 2
        self.offset_y2 = 4
        self.car_widht = 83
        self.car_height = 58
        self.gates = gates

        self.cars_row = 0
        self.cars_col = 0
        self.car_number = i % 10

        if i % 20 > 9:
            self.cars_col = 1
            self.offset_y1 = self.offset_y2

        self.rect = pygame.Rect(self.offset_x1 + self.cars_col * (self.offset_x2 + self.car_widht),
                                self.offset_y1 + self.car_number*(self.offset_y2 + self.car_height), self.car_widht, self.car_height)

        cars_img = pygame.transform.rotate(carsIMG, -90)
        self.car_img = cars_img.subsurface(self.rect)

        self.img = pygame.Surface(self.rect.size)
        self.rotate_surface = self.img

        self.angle = 0
        self.speed = 0

        self.x = 100 * (self.car_number % 10)
        self.y = 100
        if i > 9:
            self.y = 600

        self.x = 600
        self.y = 825
        self.center = [self.x + self.car_widht /
                       2, self.y + self.car_height / 2]
        self.radars = []
        self.radards_for_draw = []
        self.is_alive = True
        self.goal = False
        self.distance = 0
        self.time_spent = 0
        self.MAX_SPEED = 25
        self.next_gate = 0

    def get_current_gate(self):
        return self.gates[self.next_gate]

    def speedUp(self):
        self.speed += 1

    def speedDown(self):
        self.speed -= 1
        if self.speed < 0:
            self.speed = 0

    def update(self):

        # self.rotate_surface = self.rot_center(self.angle)
        self.rot_center(self.angle)
        self.x += math.cos(math.radians(360 - self.angle)) * self.speed
        if self.x < 20:
            self.x = 20
        elif self.x > WIN_WIDTH - self.car_widht:
            self.x = WIN_WIDTH - self.car_widht

        self.y += math.sin(math.radians(360 - self.angle)) * self.speed
        if self.y < 20:
            self.y = 20
        elif self.y > WIN_HEIGHT - self.car_height:
            self.y = WIN_HEIGHT - self.car_height

        self.center = [int(self.x + self.car_widht /
                           2), int(self.y + self.car_height / 2)]

        self.radars.clear()
        for d in range(-90, 120, 45):
            self.check_radar(d)

        # check collision with gate
        x, y, w, h = self.hitbox()
        t, b = self.get_current_gate()
        if t > b:
            c = t
            t = b
            b = c

        if (x < t[0] and x + w > t[0]) or (x > t[0] and x + w < b[0]):
            if (y > t[1] and y + h < b[1]) or (y < t[1] and y + h > b[1]):
                self.next_gate = (self.next_gate + 1) % len(self.gates)

    def hitbox(self):
        return self.rot_rect

    def draw(self, win):
        win.blit(self.rotated_image, self.rot_rect.topleft)
        pygame.draw.rect(win, (255, 0, 0), self.hitbox(), 2)

        if DEBUG == True:
            self.draw_radar(win)

    def draw_radar(self, win):

        txt_lap = STAT_FONT.render(
            f"Lap: 0/0", 1, (255, 0, 0))

        txt_gate = STAT_FONT.render(
            f"Gate: {self.next_gate}/{len(self.gates)}", 1, (255, 0, 0))

        win.blit(txt_lap, (WIN_WIDTH - 150, 10))
        win.blit(txt_gate, (WIN_WIDTH - 150, 40))

        for i, r in enumerate(self.radars):
            pos, dist = r
            pygame.draw.line(win, (0, 255, 0), self.center, pos, 1)
            pygame.draw.circle(win, (0, 255, 0), pos, 5)
            text = STAT_FONT.render(f"{i}: {dist}", 1, (255, 255, 255))
            win.blit(text, (WIN_WIDTH - 150, 70 + i * 30))

        gt = self.get_current_gate()
        pygame.draw.line(win, (0, 255, 255), self.center, gt[0], 1)
        pygame.draw.line(win, (0, 255, 255), self.center, gt[1], 1)

    def check_radar(self, degree):
        len = 0
        x = int(
            self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
        y = int(
            self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)

        while BG_IMG.get_at((x, y)) == (120, 91, 100, 255) and len < 200:
            len += 1
            x = int(
                self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
            y = int(
                self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)

        dist = int(
            math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])
        if dist < 39:
            self.is_alive = False

    def get_data(self):
        radars = self.radars
        ret = [0, 0, 0, 0, 0]
        for i, r in enumerate(radars):
            ret[i] = int(r[1] / 20)

        return ret

    def get_alive(self):
        return self.is_alive

    def get_reward(self):
        return self.distance / 50.0

    def rot_center(self, angle):
        self.rotated_image = pygame.transform.rotate(self.car_img, self.angle)
        self.rot_rect = self.rotated_image.get_rect(
            center=self.car_img.get_rect(topleft=(self.x, self.y)).center)


class GatesGenerator:
    def __init__(self, background, start_pos, step, number_of_gates):
        self.background = background
        self.start_pos = start_pos
        self.step = step
        self.number_of_gates = number_of_gates
        self.gates = []

    def getAllGates(self):
        return self.gates

    def getGatesToPass(self):
        gates = []

        for g in self.getAllGates():
            gates.append(g.getGate())

        return gates

    def generate(self):
        keepCreating = True
        i = 0
        while keepCreating:
            # for i in range(0, self.number_of_gates):
            gate = Gate(-1)
            if i > 0:
                gate = Gate(i, self.gates[i - 1].getNextPoint(),
                            self.background, self.gates[i - 1].center_pos, self.start_pos)

                keepCreating = self.outsideRange(
                    self.gates[i - 1].getNextPoint(), self.start_pos)
            else:
                gate = Gate(i, self.start_pos, self.background)

            gate.calculatePos()
            if i == 1:
                self.start_pos = self.gates[i - 1].center_pos

            self.gates.append(gate)
            i += 1

            keepCreating = not gate.finished

    def outsideRange(self, point, circleXY, radius=125):
        x1, y1 = point
        x, y = circleXY
        return math.pow(x1 - x, 2) + math.pow(y1 - y, 2) > math.pow(radius, 2)


class Gate:
    def __init__(self, number, pos=(0, 0), background="NONE", prev_pos=(0.0, 0.0), meta=(0, 0)):
        self.number = number
        self.pos = pos
        self.prev_pos = prev_pos
        self.background = background
        self.track_color = (0, 0, 0)
        self.surround = []
        self.center_pos = (0, 0)
        self.maxDist = ((0, 0), 0)
        self.meta = meta
        self.finished = False

    def calculatePos(self):
        self.track_color = self.background.get_at(self.pos)
        self.center_pos = self.center()
        self.CalcMaxDist()

        dist = math.sqrt(
            math.pow(self.meta[0] - self.center_pos[0], 2) + math.pow(self.meta[1] - self.center_pos[1], 2))

        if dist <= (RADIUS_LENGTH - 20):
            self.finished = True

    def canContinue(self):
        return self.maxDist[1][0] != 0

    def center(self):
        self.surround.clear()
        dist = []
        for d in range(0, 360, 10):
            dist.append(self.check_surroundings(d))

        md = min(dist)
        for i, s in enumerate(self.surround):
            if s[1] == md:
                self.minDist = s
                startAngle = (i + 14) % 36
                endAngle = (startAngle + 9) % 36

                minDistOpposite = RADIUS_LENGTH
                while startAngle % 36 != endAngle % 36:
                    if minDistOpposite > self.surround[startAngle % 36][1]:
                        self.minDist180 = self.surround[startAngle % 36]
                        minDistOpposite = self.surround[startAngle % 36][1]
                    startAngle = (startAngle + 1) % 36

        return (int((self.minDist[0][0] + self.minDist180[0][0])/2), int((self.minDist[0][1] + self.minDist180[0][1])/2))

    def CalcMaxDist(self):
        maxD = 0

        for i, s in enumerate(self.surround):
            if s[1] > maxD and self.outsideRange(s[0]) and self.allPointsOnTrack(s[0]):
                maxD = s[1]
                self.maxDist = s

    def outsideRange(self, point, radius=180):
        x1, y1 = point
        x, y = self.prev_pos
        return math.pow(x1 - x, 2) + math.pow(y1 - y, 2) > math.pow(radius, 2)

    def findPointInCircle(self, point, radius=5):
        circle = []
        y = -radius + point[1]
        while y <= radius + + point[1]:
            circle.append((int(point[0]), int(y)))
            y += 1

        sqRadius = radius * radius
        h = radius
        dx = 1
        while dx <= radius:
            while dx * dx + h * h > sqRadius and h > 0:
                h -= 1

            y = -h + point[1]
            while y <= h + point[1]:
                circle.append((int(point[0] + dx), int(y)))
                circle.append((int(point[0] - dx), int(y)))
                y += 1

            dx += 1

        return circle

    def onTrack(self, circle):
        for p in circle:
            if p[0] >= 0 and p[0] <= WIN_WIDTH and p[1] >= 0 and p[1] <= WIN_HEIGHT:
                if self.background.get_at(p) != self.track_color:
                    return False

        return True

    def getNextPoint(self):
        x = int(self.maxDist[0][0])
        y = int(self.maxDist[0][1])

        return (x, y)

    def allPointsOnTrack(self, pos):
        circle = self.findPointInCircle(pos)
        circle_ok = self.onTrack(circle)

        line = [(x, y) for (x, y) in self.BresenhamsLineAlgorithm(pos)]

        line_ok = self.onTrack(line)

        return circle_ok and line_ok

    # Bresenhams line algorithm
    def BresenhamsLineAlgorithm(self, pos):
        x0, y0 = self.center_pos
        x1, y1 = pos
        x1 = int(x1)
        y1 = int(y1)

        deltax = x1-x0
        if x1 == x0:
            return (0, 0)
        else:
            dxsign = int(abs(deltax)/deltax)

        deltay = y1-y0
        if y1 == y0:
            dysign = 0
        else:
            dysign = int(abs(deltay)/deltay)

        if deltay == deltax or deltax == 0:
            deltaerr = 0
        else:
            deltaerr = abs(deltay/deltax)

        error = 0
        y = y0
        for x in range(x0, x1, dxsign):
            yield x, y
            error = error + deltaerr
            while error >= 0.5:
                y += dysign
                error -= 1
        yield x1, y1

    def check_surroundings(self, degree):
        len = 0
        x = self.pos[0] + math.cos(math.radians(360 - degree)) * len
        y = self.pos[1] + math.sin(math.radians(360 - degree)) * len
        onScreen = True

        while onScreen and self.background.get_at((int(x), int(y))) == self.track_color and len < RADIUS_LENGTH:
            len += 1
            x = self.pos[0] + math.cos(math.radians(360 - degree)) * len
            y = self.pos[1] + math.sin(math.radians(360 - degree)) * len

            if x >= 0 and x <= WIN_WIDTH and y >= 0 and y <= WIN_HEIGHT:
                onScreen = True
            else:
                onScreen = False

        dist = math.sqrt(
            math.pow(x - self.pos[0], 2) + math.pow(y - self.pos[1], 2))

        self.surround.append([(x, y), dist])
        return dist

    def draw(self, win):
        # pygame.draw.circle(win, (255, 0, 0), self.center_pos, 5)
        lineColor = (255, 0, 0)
        if self.finished == True:
            lineColor = (255, 0, 255)

        for s in self.surround:
            # if s == self.maxDist and not self.finished:
            #     pygame.draw.line(win, lineColor, self.center_pos, s[0])

            if s == self.minDist or s == self.minDist180:
                pygame.draw.line(win, lineColor, self.center_pos, s[0])

        if self.finished == True:
            pygame.draw.line(win, (255, 255, 0), self.center_pos, self.meta)

    def getGate(self):
        return (self.minDist[0], self.minDist180[0])


def main():
    run = True
    clock = pygame.time.Clock()

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    background = BG_IMG.convert()

    gatesGen = GatesGenerator(background, (700, 825), 100, 30)
    gatesGen.generate()
    toPass = gatesGen.getGatesToPass()

    cars_img = CARS.convert_alpha()
    cars = [Car(cars_img, 19, toPass)]

    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Closing game...")
                run = False
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    cars[0].speed += 1
                    print("Speed: " + str(cars[0].speed))
                if event.key == pygame.K_LEFT:
                    cars[0].speed -= 1
                    print("Speed: " + str(cars[0].speed))
                if event.key == pygame.K_UP:
                    cars[0].angle += 10
                    print("Angle: " + str(cars[0].angle))
                if event.key == pygame.K_DOWN:
                    cars[0].angle -= 10
                    print("Angle: " + str(cars[0].angle))

        for car in cars:
            car.update()

        draw_window(win, BG_IMG, cars, gatesGen.getAllGates())


def draw_window(win, BG, cars, gates=[]):
    win.blit(BG, (0, 0))

    for gate in gates:
        gate.draw(win)

    for car in cars:
        car.draw(win)

    pygame.display.update()


def eval_genomes(genomes, config):
    nets = []
    cars = []
    ge = []

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    background = BG_IMG.convert()
    cars_img = CARS.convert_alpha()

    run = True
    clock = pygame.time.Clock()

    for id, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0
        ge.append(g)

        cars.append(Car(cars_img, id))

    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Closing game...")
                run = False
                pygame.quit()
                quit()

        if len(cars) == 0:
            run = False
            break

        for index, car in enumerate(cars):
            car.update()

            output = nets[index].activate(car.get_data())

            if output[0] > 0.5:
                car.angle += 10
            elif output[0] < -0.5:
                car.angle -= 10

            if output[1] > 0.5:
                car.speedUp()
            elif output[1] < -0.5:
                car.speedDown()

            if not car.is_alive:
                ge[index].fitness -= 1
                cars.pop(index)
                nets.pop(index)
                ge.pop(index)

            if car.speed > 5:
                ge[index].fitness += 0.1

            if car.speed > 10:
                ge[index].fitness += 0.1

        draw_window(win, background, cars)


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(neat.StatisticsReporter())

    winner = p.run(eval_genomes, 5)
    print('\nBest genome:\n{!s}'.format(winner))


# if __name__ == "__main__":
#     local_dir = os.path.dirname(__file__)
#     config_path = os.path.join(local_dir, "config-feedforward.txt")
#     run(config_path)

main()
