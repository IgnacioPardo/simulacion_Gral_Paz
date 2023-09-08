from car import Car
from highway import Highway

from utils import rotate_bound

from matplotlib import animation, pyplot as plt
from matplotlib.offsetbox import AnnotationBbox, OffsetImage

import numpy as np
import cv2

from tqdm import tqdm

import random

random.seed(42)

np.random.seed(42)


# Pass tqdm to update function animation

# Interval (Delay between frames in milliseconds) = 0
# FPS = 30
# Duration is going to be frames / fps (in seconds)
# 600 * / 30 = 20 seconds

PRECISION = 100
FRAMES = 12000
INTERVAL = 0
FPS = 30

with tqdm(total=FRAMES, desc="Frames", unit="frame") as pbar:

    agp = Highway(length=14 * 1000)

    car_colors = ["car_b", "car_y", "car_k", "car_w"]

    agp.add_car(
        Car(
            x=0,
            v=0,
            vmax=120,
            a=2,
            amax=2,
            length=5,
            tr=1,
            vd=120,
            fc=None,
            bc=None,
            will_measure=True,
        )
    )

    fig, ax = plt.subplots(figsize=(22, 2))

    # tight_layout makes sure the axis and title are not cropped
    fig.tight_layout()

    ax.set_xlim(0, agp.length)
    ax.set_ylim(-3, 12)

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


    car_ims = [
        OffsetImage(plt.imread(f"assets/{car_color}.png", format="png"), zoom=0.4)
        for car_color in car_colors
    ]


    def init():
        # Animate with AnnotationBbox for each car
        return []


    def update(frame):

        pbar.update(1)
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

        for _ in range(PRECISION):
            status = agp.update(frame)
            # agp.tow_cars(now=True)

        # if len(agp.get_cars()) < 5:
        # if np.random.uniform() < 0.1:
        if agp.get_back_car().get_position() > agp.length / np.random.normal(20, 2):

            agp.add_car(
                Car(
                    x=None,
                    v=int(np.random.uniform(40, 80)),
                    vmax=int(np.random.normal(120, 10)),
                    a=max(0, int(np.random.normal(2, 1))),
                    amax=np.random.uniform(1.5, 3),
                    length=1.5,
                    # Reaction times are between 0.4 and 1 seconds, 
                    #   Mean:  0.7316666666666668
                    #   Median:  0.725
                    #   Variance:  0.026653888888888883
                    #   Standard Deviation:  0.16326018770321465
                    #   Skewness:  -0.040838018027236994
                    tr=np.random.normal(0.7316666666666668, 0.16326018770321465),
                    vd=100,
                    fc=None,
                    bc=None,
                    will_measure=True,
                    car_id=len(agp.get_cars()),
                )
            )

        if not status:
            # Stop animation
            # return []
            pass

        artists = []

        for car in agp.get_cars()[::-1]:

            x = car.get_position()
            # v = car.v

            # car_color = car_colors[car.id % len(car_colors)]
            # if car.crashed:
            #   car_color = 'car_r'

            car_color = "car_r" if car.crashed else car_colors[car.id % len(car_colors)]

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
        adata = agp.get_cars_accelerations()
        tdata = agp.get_cars_times()
        crashes = [1 if car.crashed else 0 for car in agp.get_cars()]
        ids = [car.id for car in agp.get_cars()]

        # Plot car velocities and positions as text
        ax.text(0.1, 0.9, f"Accelerations: {adata}", transform=ax.transAxes)
        ax.text(0.1, 0.8, f"Velocities: {vdata}", transform=ax.transAxes)
        ax.text(0.1, 0.7, f"Positions: {xdata}", transform=ax.transAxes)
        ax.text(0.1, 0.6, f"Times: {tdata}", transform=ax.transAxes)
        ax.text(0.1, 0.5, f"Crashes: {crashes}", transform=ax.transAxes)
        ax.text(0.1, 0.4, f"IDs: {ids}", transform=ax.transAxes)

        # Plot Frame number
        ax.text(0.02, 0.9, f"Frame: {frame}", transform=ax.transAxes)

        # Set font family and font size
        for txt in ax.texts:
            txt.set_fontfamily("monospace")
            # txt.set_fontsize(10)

        return artists


    

    # ani = animation.FuncAnimation(
    #     fig, update, frames=FRAMES, init_func=init, blit=True, interval=INTERVAL
    # )

    # ani.save(
    #     "animation.mp4", fps=FPS, extra_args=["-vcodec", "libx264", "-pix_fmt", "yuv420p"]
    # )

    ani = animation.FuncAnimation(
        fig, update, frames=FRAMES, init_func=init, blit=True, interval=INTERVAL
    )

    ani.save(
        "animation.mp4",
        fps=FPS,
        extra_args=["-vcodec", "libx264", "-pix_fmt", "yuv420p"],
    )


    # ax.set_xlim(0, 1000)
    # plt.show()
