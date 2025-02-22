"""MANDELBROT"""
import os
import threading
# import cmath
# import random as rnd
import pygame as pg
import numpy as np

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_BACKGROUND = COLOR_WHITE

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900
SCREEN_FPS = 60

mandelbrot_max_check_iter = 200

field_topleft: complex = None
INIT_SCALE = 2.0/SCREEN_HEIGHT
field_scale: float = None

running = True
need_redraw = False
field_np: np.array = None
th: threading.Thread = None
stop_event = threading.Event()
stop_event.set()


def goto_home():
    goto_point(complex(-0.5, 0), INIT_SCALE)


def goto_point(center: complex, scale: float):
    """центрирование на точке с нужным масштабом"""
    global field_topleft
    global field_scale
    field_scale = scale
    field_topleft = center+complex(-field_scale*SCREEN_WIDTH/2,
                                   field_scale*SCREEN_HEIGHT/2)
    recalculate()


def recalculate(new_field: bool = True) -> None:
    global stop_event
    global th
    global field_np
    global need_redraw
    global mandelbrot_max_check_iter

    print("recalculate STARTED")
    stop_event.set()

    if new_field:
        field_np = np.full((SCREEN_WIDTH, SCREEN_HEIGHT),
                           0, dtype=int)
    else:
        if mandelbrot_max_check_iter < 200:
            mandelbrot_max_check_iter += 50
    stop_event = threading.Event()
    th = threading.Thread(target=calculate_field,
                          daemon=True, args=(stop_event, field_np))
    th.start()
    set_caption()
    need_redraw = True


def get_mandelbrot_rate(c: complex, max_check_iter: int = 100) -> tuple[bool, int]:
    z = complex(0.0, 0.0)
    for i in range(1, max_check_iter):
        z = z**2 + c
        if abs(z) > 2.0:
            return (False, i)
    return (True, max_check_iter)


def handle_events():
    global field_topleft
    global field_scale

    for event in pg.event.get():
        if event.type == pg.QUIT:
            return False

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                return False
            if event.key == pg.K_HOME:
                goto_home()

        if event.type == pg.MOUSEBUTTONUP:
            pos = pg.mouse.get_pos()
            # print (pos)
            point = complex(
                field_topleft.real+pos[0]*field_scale,
                field_topleft.imag-pos[1]*field_scale)
            print(point)
            goto_point(point, field_scale/5.0)

    #     if event.type != pg.MOUSEMOTION:
    #         # print(f"{draw_scene.left} {draw_scene.top}")
    #         pass

    # keys = pg.key.get_pressed()
    # if keys[pg.K_LEFT]:
    #     draw_scene.left -= 1
    # elif keys[pg.K_RIGHT]:
    #     draw_scene.left += 1
    # elif keys[pg.K_UP]:
    #     draw_scene.top -= 1
    # elif keys[pg.K_DOWN]:
    #     draw_scene.top += 1

    return True


def calculate_field(stop_event, arr: np.array):
    global need_redraw
    global mandelbrot_max_check_iter
    print("calculate_field STARTED")
    for j in range(SCREEN_HEIGHT):
        for i in range(SCREEN_WIDTH):
            if (not running) or stop_event.is_set():
                return
            c = complex(field_topleft.real+field_scale*i,
                        field_topleft.imag-field_scale*j)
            _, k = get_mandelbrot_rate(c, mandelbrot_max_check_iter)
            arr[i, j] = k
        need_redraw = True
        # print(f'{c} - {b}')
    print("calculate_field DONE")
    # recalculate(False)


def draw_scene(sc: pg.Surface):
    global need_redraw
    if need_redraw:
        need_redraw = False
        sc.fill(COLOR_BACKGROUND)
        for i in range(SCREEN_WIDTH):
            for j in range(SCREEN_HEIGHT):
                if field_np[i, j] >= mandelbrot_max_check_iter:
                    sc.set_at((i, j), COLOR_BLACK)
                elif field_np[i, j] < 255:
                    sc.set_at(
                        (i, j), (255-field_np[i, j], 255-field_np[i, j], 255-field_np[i, j]))

        pg.display.update()


def set_caption():
    pg.display.set_caption(
        f'Field: {field_topleft} - '
        f'{complex(
            field_topleft.real+field_scale*SCREEN_WIDTH,
            field_topleft.imag-field_scale*SCREEN_HEIGHT)} Scale: {INIT_SCALE/field_scale:.{2}f} Iter: {mandelbrot_max_check_iter}')


def main():
    global running
    global th

    pg.init()
    sc = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pg.time.Clock()
    goto_home()

    while running:
        clock.tick(SCREEN_FPS)
        running = handle_events()
        draw_scene(sc)
        if not running:
            stop_event.set()
    pg.quit()


if __name__ == '__main__':
    main()
