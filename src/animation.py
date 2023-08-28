import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from random import randint
import numpy as np

# set random seed
import random

random.seed(42)

np.random.seed(42)

import cv2

from car import Car
from highway import Highway


def rotate_bound(image, angle):
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)

    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY

    # perform the actual rotation and return the image
    return cv2.warpAffine(image, M, (nW, nH), borderValue=(255, 255, 255))


car_colors = ["car_r", "car_y", "car_b", "car_k", "car_w"]

agp = Highway(length=14 * 1000)
agp.add_car(Car(x=0  , v=0, vmax=120, a=14, l=5, tr=1, vd=120, fc=None, bc=None, will_measure=True))
agp.add_car(Car(x=100, v=0, vmax=100, a=3, l=5, tr=1, vd=120, fc=None, bc=None, will_measure=True))
agp.add_car(Car(x=200, v=0, vmax=110, a=4, l=5, tr=1, vd=120, fc=None, bc=None, will_measure=True))
agp.add_car(Car(x=300, v=0, vmax=150, a=3, l=5, tr=1, vd=120, fc=None, bc=None, will_measure=True))
agp.add_car(Car(x=400, v=0, vmax=200, a=100, l=5, tr=1, vd=1000, fc=None, bc=None, will_measure=True))

# Add more cars
# for i in range(30):
#    agp.add_car(Car(x=500 + i*100, v=0, vmax=120 + i*2, a=5, l=5, tr=1, vd=120, fc=None, bc=None, will_measure=True))

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
    plt.imread(f"assets/{car_color}.png", format="png") for car_color in car_colors
]


def init():
    return []


def update(frame):

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
    """ 
    if agp.get_back_car().get_position() > agp.length / 10:

        agp.add_car(
            Car(x=None, v=0, 
            #vmax=2,
            vmax=int(np.random.normal(120, 10)),
            a=int(np.random.normal(5, 2)),
            l=1.5, tr=1, vd=10, fc=None, bc=None, will_measure=True)
        ) """

    if not status:
        # Stop animation
        # return []
        pass

    artists = []

    for car in agp.get_cars()[::-1]:
        x = car.get_position()
        v = car.v

        car_im = car_ims[car.id % len(car_ims)]

        if v > 140:
            angle = -20 * np.sin(2 * np.pi * frame / 100)
            car_im = rotate_bound(car_im, angle)

        car_oi = OffsetImage(car_im, zoom=0.4)
        ab = AnnotationBbox(car_oi, (x, 0), frameon=False)

        artists.append(ax.add_artist(ab))

    xdata = agp.get_cars_positions()
    vdata = agp.get_cars_velocities()
    tdata = agp.get_cars_times()

    # Plot car velocities and positions as text
    ax.text(0.1, 0.9, f"Velocities: {vdata}", transform=ax.transAxes)
    ax.text(0.1, 0.8, f"Positions: {xdata}", transform=ax.transAxes)
    ax.text(0.1, 0.7, f"Times: {tdata}", transform=ax.transAxes)

    # set font family and font size
    for txt in ax.texts:
        txt.set_fontfamily("monospace")

    return artists


ani = animation.FuncAnimation(
    fig, update, frames=500, init_func=init, blit=True, interval=25
)

# save the animation as an mp4.  This requires ffmpeg

# -vcodec defines the codec to use.
# -pix_fmt defines the pixel format.
# yuv420p specifies the planar 4:2:0 YUV full scale. This should also work on most other platforms.
# libx264 specifies the H.264/MPEG-4 AVC encoder.

# ani.save('animation.mp4', fps=30, extra_args=['-vcodec', 'libx264', '-pix_fmt', 'yuv420p'])

# Show animation in real time
# plt.show() with fps=30
plt.show()
