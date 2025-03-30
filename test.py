import pygame
import math
import random


class Balloon:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.radius = random.randint(20, 40)
        self.mass = self.radius * 0.5
        self.x = random.uniform(self.radius, screen_width - self.radius)
        self.y = random.uniform(self.radius, screen_height * 0.3)
        self.vx = (random.random() - 0.5) * 2
        self.vy = random.random() * 2 + 1
        self.color = (random.randint(100, 255),
                      random.randint(100, 255),
                      random.randint(100, 255))

    def update(self, gravity, shake_force):
        # 应用晃动力
        self.vx += shake_force[0] / self.mass
        self.vy += shake_force[1] / self.mass

        # 基础物理
        self.vy += gravity
        self.vx *= 0.98  # 空气阻力
        self.vy *= 0.98

        self.x += self.vx
        self.y += self.vy

        # 边界碰撞
        if self.x < self.radius:
            self.x = self.radius
            self.vx *= -0.8
        if self.x > self.screen_width - self.radius:
            self.x = self.screen_width - self.radius
            self.vx *= -0.8
        if self.y < self.radius:
            self.y = self.radius
            self.vy = abs(self.vy) * 0.8
        if self.y > self.screen_height - self.radius:
            self.y = self.screen_height - self.radius
            self.vy = -abs(self.vy) * 0.6

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        # 添加高光效果
        pygame.draw.circle(screen, (255, 255, 255),
                           (int(self.x) + self.radius // 3,
                            int(self.y) - self.radius // 3),
                           self.radius // 4)


class ShakeSimulator:
    def __init__(self):
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height),
                                              pygame.RESIZABLE)
        pygame.display.set_caption("晃动气球模拟器")
        self.clock = pygame.time.Clock()

        # 初始化气球
        self.balloons = [Balloon(self.screen_width, self.screen_height)
                         for _ in range(15)]

        # 晃动参数
        self.shake_force = [0, 0]  # X/Y方向晃动力
        self.gravity = 0.5
        self.last_mouse_pos = (0, 0)
        self.shake_sensitivity = 0.8  # 晃动灵敏度

        # 性能优化
        self.last_shake_time = 0
        self.fps = 60

    def handle_events(self):
        current_shake = [0, 0]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.VIDEORESIZE:
                # 窗口大小变化时更新参数
                self.screen_width, self.screen_height = event.size
                self.screen = pygame.display.set_mode((self.screen_width,
                                                       self.screen_height),
                                                      pygame.RESIZABLE)
            elif event.type == pygame.MOUSEMOTION:
                # 根据鼠标移动速度计算晃动力
                rel_x, rel_y = event.rel
                current_shake[0] += rel_x * self.shake_sensitivity
                current_shake[1] += rel_y * self.shake_sensitivity

        # 平滑处理晃动力
        self.shake_force = [
            0.7 * self.shake_force[0] + 0.3 * current_shake[0],
            0.7 * self.shake_force[1] + 0.3 * current_shake[1]
        ]
        return True

    def handle_collisions(self):
        for i in range(len(self.balloons)):
            for j in range(i + 1, len(self.balloons)):
                dx = self.balloons[j].x - self.balloons[i].x
                dy = self.balloons[j].y - self.balloons[i].y
                distance = math.hypot(dx, dy)
                min_dist = self.balloons[i].radius + self.balloons[j].radius

                if distance < min_dist:
                    # 碰撞处理
                    angle = math.atan2(dy, dx)
                    overlap = (min_dist - distance) / 2

                    # 位置修正
                    self.balloons[i].x -= math.cos(angle) * overlap
                    self.balloons[i].y -= math.sin(angle) * overlap
                    self.balloons[j].x += math.cos(angle) * overlap
                    self.balloons[j].y += math.sin(angle) * overlap

                    # 动量交换
                    mass_sum = self.balloons[i].mass + self.balloons[j].mass
                    vx1 = (self.balloons[i].vx * (self.balloons[i].mass - self.balloons[j].mass) + \
                           2 * self.balloons[j].mass * self.balloons[j].vx) / mass_sum
                    vy1 = (self.balloons[i].vy * (self.balloons[i].mass - self.balloons[j].mass) + \
                           2 * self.balloons[j].mass * self.balloons[j].vy) / mass_sum
                    vx2 = (self.balloons[j].vx * (self.balloons[j].mass - self.balloons[i].mass) + \
                           2 * self.balloons[i].mass * self.balloons[i].vx) / mass_sum
                    vy2 = (self.balloons[j].vy * (self.balloons[j].mass - self.balloons[i].mass) + \
                           2 * self.balloons[i].mass * self.balloons[i].vy) / mass_sum

                    self.balloons[i].vx, self.balloons[i].vy = vx1, vy1
                    self.balloons[j].vx, self.balloons[j].vy = vx2, vy2

    def run(self):
        running = True
        while running:
            delta_time = self.clock.get_time() / 1000  # 获取帧时间（秒）

            # 事件处理
            running = self.handle_events()

            # 更新物理
            for balloon in self.balloons:
                balloon.update(self.gravity, self.shake_force)
            self.handle_collisions()

            # 渲染
            self.screen.fill((30, 30, 50))  # 深空背景色
            for balloon in self.balloons:
                balloon.draw(self.screen)

            # 显示调试信息
            font = pygame.font.SysFont("Arial", 20)
            debug_text = [
                f"气球数量: {len(self.balloons)}",
                f"晃动力度: X:{self.shake_force[0]:.1f} Y:{self.shake_force[1]:.1f}",
                f"帧率: {self.clock.get_fps():.1f} FPS",
                "[鼠标拖动窗口进行晃动]"
            ]
            y_pos = 10
            for text in debug_text:
                surface = font.render(text, True, (200, 200, 255))
                self.screen.blit(surface, (10, y_pos))
                y_pos += 25

            pygame.display.flip()
            self.clock.tick(self.fps)


if __name__ == "__main__":
    simulator = ShakeSimulator()
    simulator.run()
    pygame.quit()