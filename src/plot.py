from car import Car
from highway import Highway

from utils import rotate_bound

from matplotlib import animation, pyplot as plt
from matplotlib.offsetbox import AnnotationBbox, OffsetImage

import numpy as np
import cv2


agp = Highway(length=14 * 1000)

car_colors = ["car_y", "car_b", "car_k", "car_w"]

fig, ax = plt.subplots(figsize=(22, 2))

ax.set_xlim(0, agp.length)
ax.set_ylim(-3, 10)

# ax hide y axis
ax.set_yticks([])

lw = 4
# Plot lane lines
ax.plot([2, agp.length], [lw / 2, lw / 2], color="black", linewidth=2)
ax.plot([2, agp.length], [-lw / 2, -lw / 2], color="black", linewidth=2)

# Plot asphalt area
ax.fill_between(
    [2, agp.length], [-lw / 2, -lw / 2], [lw / 2, lw / 2], color="lightgrey"
)

# Plot dashed center line
ax.plot(
    [2, agp.length],
    [0, 0],
    color="white",
    linewidth=2,
    linestyle="dashed",
    dashes=(5, 5),
)

angle = -20
car_ims = [
    OffsetImage(
        rotate_bound(
            cv2.imread(f"assets/{car_color}.png", cv2.IMREAD_UNCHANGED), angle
        ),
        zoom=0.4,
    )
    for car_color in car_colors
]

car_anots = [
    AnnotationBbox(car_im, (1000 * (i + 2), 0), frameon=False)
    for i, car_im in enumerate(car_ims)
]

# add car to plot
for car_anot in car_anots:
    ax.add_artist(car_anot)

plt.show()

agp.add_car(
    Car(x=0, v=0, vmax=120, a=2, l=5, tr=1, vd=120, fc=None, bc=None, will_measure=True)
)
agp.add_car(
    Car(x=100, v=0, vmax=100, a=2, l=5, tr=1, vd=120, fc=None, bc=None, will_measure=True,
    )
)
agp.add_car(
    Car(x=200, v=0, vmax=110, a=2, l=5, tr=1, vd=120, fc=None, bc=None, will_measure=True,
    )
)
agp.add_car(
    Car(x=300, v=0, vmax=150, a=2, l=5, tr=1, vd=120, fc=None, bc=None, will_measure=True,
    )
)
agp.add_car(
    Car(x=400, v=0, vmax=200, a=2, l=5, tr=1, vd=1000, fc=None, bc=None, will_measure=True,
    )
)

# Add more cars
for i in range(30):
    agp.add_car(
        Car(x=500 + i * 100, v=0, vmax=120 + i * 2, a=2, l=5, tr=1, vd=120, fc=None, bc=None, will_measure=True,
        )
    )

fig, ax = plt.subplots(figsize=(22, 2))

# tight_layout makes sure the axis and title are not cropped
fig.tight_layout()

ax.set_xlim(0, agp.length)
ax.set_ylim(-3, 10)

# ax hide y axis
ax.set_yticks([])

# Hide the right and top spines
# ax.spines['left'].set_visible(False)
# ax.spines['top'].set_visible(False)
# ax.spines['bottom'].set_visible(False)

lw = 4
# Plot lane lines
ax.plot([2, agp.length], [lw / 2, lw / 2], color="black", linewidth=2)
ax.plot([2, agp.length], [-lw / 2, -lw / 2], color="black", linewidth=2)

# Plot asphalt area
ax.fill_between(
    [2, agp.length], [-lw / 2, -lw / 2], [lw / 2, lw / 2], color="lightgrey"
)

# Plot dashed center line
ax.plot(
    [2, agp.length],
    [0, 0],
    color="white",
    linewidth=2,
    linestyle="dashed",
    dashes=(5, 5),
)

# car_im = OffsetImage(plt.imread('assets/car_y.png', format="png"), zoom=.2)

car_ims = [
    OffsetImage(plt.imread(f"assets/{car_color}.png", format="png"), zoom=0.4)
    for car_color in car_colors
]


def init():
    # Animate with AnnotationBbox for each car
    return []


def update(frame):
    # Once per frame
    # One frame is one second

    # Delete previous rendered cars
    for artist in ax.artists:
        artist.remove()

    # Clear previous text
    # ax.texts = [] AttributeError: can't set attribute
    # fix
    for txt in ax.texts:
        # txt.set_visible(False)
        txt.remove()

    status = agp.update()

    # if len(agp.get_cars()) < 5:
    if agp.get_back_car().get_position() > agp.length / np.random.normal(20, 2):

        agp.add_car(
            Car(
                x=None,
                v=0,
                # vmax=2,
                vmax=int(np.random.normal(120, 10)),
                a=int(np.random.normal(2, 1)),
                l=1.5,
                tr=1,
                vd=10,
                fc=None,
                bc=None,
                will_measure=True,
            )
        )

    if not status:
        # Stop animation
        # return []
        pass

    artists = []

    for car in agp.get_cars()[::-1]:

        x = car.get_position()
        v = car.v

        car_color = car_colors[car.id % len(car_colors)]
        # if car.crashed:
        #    car_color = 'car_r'
        # car_im = #cv2.imread(f'assets/{car_color}.png', cv2.IMREAD_UNCHANGED)
        car_im = plt.imread(f"assets/{car_color}.png", format="png")

        # Drift: sacar
        # if v > 140:
        #   angle = -20 * np.sin(2 * np.pi * frame / 100)
        #   car_im = rotate_bound(car_im, angle)

        car_oi = OffsetImage(car_im, zoom=0.4)
        ab = AnnotationBbox(car_oi, (x, 0), frameon=False)

        artists.append(ax.add_artist(ab))

    xdata = agp.get_cars_positions()
    vdata = agp.get_cars_velocities()
    tdata = agp.get_cars_times()
    crashes = [1 if car.crashed else 0 for car in agp.get_cars()]
    ids = [car.id for car in agp.get_cars()]

    # Plot car velocities and positions as text
    ax.text(0.1, 0.9, f"Velocities: {vdata}", transform=ax.transAxes)
    ax.text(0.1, 0.8, f"Positions: {xdata}", transform=ax.transAxes)
    ax.text(0.1, 0.7, f"Times: {tdata}", transform=ax.transAxes)
    ax.text(0.1, 0.6, f"Crashes: {crashes}", transform=ax.transAxes)
    ax.text(0.1, 0.5, f"IDs: {ids}", transform=ax.transAxes)

    # set font family and font size
    for txt in ax.texts:
        txt.set_fontfamily("monospace")
        # txt.set_fontsize(10)

    return artists


FRAMES = 500
INTERVAL = 0
FPS = 30

# Frames = 500
# Interval (Delay between frames in milliseconds) = 0
# FPS = 30
# Duration is going to be frames * (1 / fps) (in seconds)
# 500 * (1 / 30) = 16.666666666666668 seconds

FRAMES = 60
INTERVAL = 0
FPS = 1

ani = animation.FuncAnimation(
    fig, update, frames=FRAMES, init_func=init, blit=True, interval=INTERVAL
)
ani.save(
    "animation.mp4", fps=FPS, extra_args=["-vcodec", "libx264", "-pix_fmt", "yuv420p"]
)
