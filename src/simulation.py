"""
Simulation of Avenida General Paz (AGP) from Liniers to Lugano in Buenos Aires, Argentina.
Single lane, 14 km long, 100 km/h speed limit, mean of 1.5 m long cars.

The simulation is based on the Intelligent Driver Model (IDM).

"""

from car import Car
from highway import Highway

from matplotlib import animation, pyplot as plt
from matplotlib.offsetbox import AnnotationBbox, OffsetImage

import numpy as np
import pandas as pd

import os
from datetime import datetime

# import cv2
# from utils import rotate_bound

from tqdm import tqdm

import random

import argparse

parser = argparse.ArgumentParser(description="Simulate a highway")

parser.add_argument(
    "--precision", type=int, help="Precision of the simulation", default=100
)
parser.add_argument(
    "--frames", type=int, help="Number of frames to simulate", default=12000
)
parser.add_argument(
    "--interval", type=int, help="Interval between frames in milliseconds", default=0
)
parser.add_argument("--fps", type=int, help="Frames per second", default=30)
parser.add_argument(
    "--length", type=int, help="Length of the highway in meters", default=14 * 1000
)
parser.add_argument(
    "--max_v", type=int, help="Maximum velocity of the cars in km/h", default=100
)
parser.add_argument("--plot", type=bool, help="Plot the simulation", default=False)
parser.add_argument("--live", type=bool, help="Plot the simulation live", default=False)
parser.add_argument(
    "--short_scale",
    type=bool,
    help="Plot the simulation with a short scale",
    default=False,
)
parser.add_argument("--log", type=bool, help="Log the simulation", default=True)
parser.add_argument(
    "--seed", type=int, help="Seed for the random number generator", default=42
)

args = parser.parse_args()

# Interval (Delay between frames in milliseconds) = 0
# FPS = 30
# Duration is going to be frames / fps (in seconds)
# 600 * / 30 = 20 seconds

PRECISION = args.precision
FRAMES = args.frames
INTERVAL = args.interval
FPS = args.fps

# Simulated Time = Frames (s)

HIGHWAY_LENGTH = args.length  # m
MAX_V = args.max_v  # km/h => Car converts to m/s

PLOT = args.plot

LIVE = args.live and PLOT
SHORT_SCALE = args.short_scale and PLOT

LOG = args.log
AGP_LOG_FILE = f"logs/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_agp_data.csv"
CARS_LOG_FILE = f"logs/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_cars_data.csv"

SEED = args.seed

random.seed(SEED)
np.random.seed(SEED)

if LOG:

    # Check if log directory exists

    if not os.path.exists("logs"):
        os.makedirs("logs")

    agp_df = pd.DataFrame(
        columns=[
            "frame",
            "current_car_count",
            "historic_car_count",
            "current_crash_count",
            "historic_crash_count",
            "avg_v",
            "avg_a",
            "avg_t_d",
        ]
    )

    times_df = pd.DataFrame(
        columns=[
            "frame",
            "car_id",
            "avg_car_v",
            "avg_car_a",
            "car_t_d",
        ]
    )

    crashes_df = pd.DataFrame(
        columns=[
            "frame",
            "car_id",
            "car_v",
            "car_a",
            "car_t_d",
        ]
    )

    def log_agp_data(agp: Highway, frame: int):
        agp_df.loc[frame] = [
            frame,
            len(agp.get_cars()),
            len(agp.historic_ids),
            agp.get_crash_count(),
            agp.historic_crash_count,
            agp.get_avg_v(),
            agp.get_avg_a(),
            agp.get_avg_trip_duration(),
        ]

    def log_car_data(car: Car, frame: int):
        times_df.loc[len(times_df)] = [
            frame,
            car.id,
            np.mean(car.historic_velocities) if len(car.historic_velocities) > 0 else 0,
            np.mean(car.historic_accelerations)
            if len(car.historic_accelerations) > 0
            else 0,
            car.time_ellapsed / PRECISION,
        ]


car_colors = ["car_b", "car_y", "car_k", "car_w", "car_g", "car_o", "car_p", "car_v"]

agp = Highway(length=HIGHWAY_LENGTH, crash_remove_delay=5000, precision=PRECISION)

avg_v = 80
avg_trip_time = HIGHWAY_LENGTH / avg_v

with tqdm(total=FRAMES, desc="Frames", unit="frame") as pbar:

    agp.add_car(
        Car(
            x=100,
            v=int(np.random.uniform(50, 80)),
            vmax=int(np.random.normal(140, 20)),
            vd=int(np.random.normal(MAX_V, 6)),
            a=max(0, int(np.random.normal(2, 1))),
            amax=np.random.uniform(1.5, 3),
            length=1.5,
            tr=np.random.normal(0.732, 0.163),
            fc=None,
            bc=None,
            will_measure=True,
        )
    )

    if PLOT:
        # Create figure and axes
        fig, ax = plt.subplots(figsize=(22, 2))

        # tight_layout makes sure the axis and title are not cropped
        fig.tight_layout()

        ax.set_xlim(0, agp.length)
        ax.set_ylim(-3, 20)

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
        # One frame is 1 second
        # In each frame the AGP is updated PRECISION times
        # The AGP updates faster than the animation

        # Update AGP PRECISION times each frame
        for sub_t in range(PRECISION):
            agp.update(frame * PRECISION + sub_t)

        # Add cars to the AGP

        # if (len(agp.get_cars()) == 0 or agp.get_back_car().get_position() > 10):
        # if (len(agp.get_cars()) == 0 or agp.get_back_car().get_position() > 100) and (np.random.poisson() == 1):
        if len(agp.get_cars()) == 0 or agp.get_back_car().get_position() > 80:
            agp.add_car(
                Car(
                    x=None,
                    v=int(np.random.uniform(50, 80)),
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
                    tr=np.random.normal(0.732, 0.163),
                    # tr=np.random.normal(0.9, 0.2),
                    # tr=0.44,
                    # tr=10,
                    vd=int(np.random.normal(100, 5)),
                    fc=None,
                    bc=None,
                    will_measure=True,
                )
            )

        # Log AGP current data
        if LOG:
            log_agp_data(agp, frame)
            for car in agp.get_cars():
                log_car_data(car, frame)

        if PLOT:

            # Gather AGP current data
            xdata = agp.get_cars_positions()
            vdata = agp.get_cars_velocities()
            adata = agp.get_cars_accelerations()
            tdata = agp.get_cars_times()
            crashes = [1 if car.crashed else 0 for car in agp.get_cars()]
            stopped = [1 if car.stopping else 0 for car in agp.get_cars()]
            ids = [car.id for car in agp.get_cars()]
            # car_count = len(agp.get_cars())
            # historic_car_count = len(agp.historic_ids)

            dis = lambda x: list(
                map(lambda x: " " * (6 - len(f"{x:.2f}")) + f"{x:.2f}", x)
            )

            # Delete previous rendered cars
            for artist in ax.artists:
                artist.remove()

            # Clear previous text
            for txt in ax.texts:
                txt.remove()

            artists = []

            # Plot each car
            for car in agp.get_cars()[::-1]:

                x = car.get_position()

                car_color = (
                    "car_r" if car.crashed else car_colors[car.id % len(car_colors)]
                )
                car_im = plt.imread(f"assets/{car_color}.png", format="png")
                car_oi = OffsetImage(car_im, zoom=0.4)
                ab = AnnotationBbox(car_oi, (x, 0), frameon=False)
                artists.append(ax.add_artist(ab))

            # Plot Frame number
            ax.text(
                0.01,
                0.9,
                f"F:{frame}/{FRAMES}",
                transform=ax.transAxes,
                fontfamily="monospace",
            )
            # Plot ammount of cars
            ax.text(
                0.01,
                0.8,
                f"# Cars: {len(agp.get_cars())}",
                transform=ax.transAxes,
                fontfamily="monospace",
            )

            # Plot crash count
            ax.text(
                0.01,
                0.7,
                f"# Crashes: {agp.get_crash_count()}",
                transform=ax.transAxes,
                fontfamily="monospace",
            )

            # Plot Front Car Speed
            ax.text(
                0.01,
                0.6,
                f"F Car V: {agp.get_front_car().get_velocity()*3.6:.2f}",
                transform=ax.transAxes,
                fontfamily="monospace",
            )

            # Plot car velocities and positions as text
            ax.text(
                0.15,
                0.9,
                f"Accelerations: {dis(adata[::-1])}",
                transform=ax.transAxes,
                fontfamily="monospace",
            )
            ax.text(
                0.15,
                0.8,
                f"Velocities   : {list(map(lambda x: ' ' * (6 - len(f'{x*3.6:.2f}')) + f'{x*3.6:.2f}', vdata[::-1]))}",
                transform=ax.transAxes,
                fontfamily="monospace",
            )
            ax.text(
                0.15,
                0.7,
                f"Times        : {dis(tdata[::-1])}",
                transform=ax.transAxes,
                fontfamily="monospace",
            )
            ax.text(
                0.15,
                0.6,
                f"Positions    : {dis(xdata[::-1])}",
                transform=ax.transAxes,
                fontfamily="monospace",
            )
            ax.text(
                0.15,
                0.5,
                f"Crashes      : {crashes[::-1]}",
                transform=ax.transAxes,
                fontfamily="monospace",
            )
            ax.text(
                0.15,
                0.4,
                f"Stopped      : {stopped[::-1]}",
                transform=ax.transAxes,
                fontfamily="monospace",
            )
            ax.text(
                0.15,
                0.3,
                f"IDs          : {ids[::-1]}",
                transform=ax.transAxes,
                fontfamily="monospace",
            )

            # Plot Avg. Acceleration
            ax.text(
                0.07,
                0.9,
                f"Avg.Cur. A: {np.mean(adata):.2f}",
                transform=ax.transAxes,
                fontfamily="monospace",
            )
            # Plot Avg. Velocity
            ax.text(
                0.07,
                0.8,
                f"Avg.Cur. V: {np.mean(vdata)*3.6:.2f}",
                transform=ax.transAxes,
            )
            # Plot Avg. Trip Duration
            ax.text(
                0.07,
                0.7,
                f"Avg.Cur. T: {np.mean(tdata):.2f}",
                transform=ax.transAxes,
                fontfamily="monospace",
            )

            # Plot Avg. Acceleration
            ax.text(
                0.07,
                0.5,
                f"Avg.H. A: {agp.get_avg_a():.2f}",
                transform=ax.transAxes,
                fontfamily="monospace",
            )
            # Plot Avg. Velocity
            ax.text(
                0.07,
                0.4,
                f"Avg.H. V: {agp.get_avg_v()*3.6:.2f}",
                transform=ax.transAxes,
                fontfamily="monospace",
            )
            # Plot Avg. Trip Duration
            ax.text(
                0.07,
                0.3,
                f"Avg. Dur: {agp.get_avg_trip_duration():.2f}",
                transform=ax.transAxes,
                fontfamily="monospace",
            )

            return artists

        pbar.set_postfix(
            cars=f"{len(agp.get_cars())}",
            crashes=f"{agp.get_crash_count()}",
            all_cars=f"{len(agp.historic_ids)}",
            avg_v=f"{agp.get_avg_v()*3.6:.2f}",
            avg_a=f"{agp.get_avg_a():.2f}",
            avg_t_d=f"{agp.get_avg_trip_duration():.2f}",
            avg_h_v=f"{agp.get_avg_v()*3.6:.2f}",
            avg_h_a=f"{agp.get_avg_a():.2f}",
            avg_h_t_d=f"{agp.get_avg_trip_duration():.2f}",
        )

        return None

    if PLOT:

        if SHORT_SCALE:
            ax.set_xlim(1000, 1200)
            FPS = 5

        if LIVE:
            ani = animation.FuncAnimation(
                fig, update, frames=FRAMES, init_func=init, blit=True, interval=1
            )
            plt.show()

        else:

            ani = animation.FuncAnimation(
                fig, update, frames=FRAMES, init_func=init, blit=True, interval=INTERVAL
            )

            ani.save(
                "animation.mp4",
                fps=FPS,
                extra_args=["-vcodec", "libx264", "-pix_fmt", "yuv420p"],
            )

    else:
        for frame in tqdm(range(FRAMES)):
            update(frame)

            if LOG and frame % 100 == 0:
                # Save data to CSV
                agp_df.to_csv(AGP_LOG_FILE)
                times_df.to_csv(CARS_LOG_FILE)
