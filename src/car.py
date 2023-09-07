from random import randint
from typing import Optional


class Car:
    def __init__(
        self,
        x: float,
        v: float,
        vmax: float,
        a: float,
        l: float,
        tr: float,
        vd: float,
        bc: "Car",
        fc: Optional["Car"] = None,
        will_measure: Optional[bool] = False,
    ):
        self.id = id(self)

        self.t = 0

        # Internally, we use SI units
        # Position in meters
        # Velocity in m/s
        # Acceleration is in m/s^2

        # Externally, we use km/h for velocity
        # But we convert it to m/s internally

        self.x = x

        self.v = v / 3.6

        self.vmax = vmax

        self.a = a
        self.length = l

        self.reaction_time = tr
        self.desired_velocity = vd

        self.f_car = fc
        self.b_car = bc

        self.will_measure = will_measure

        self.crashed = False

    def __str__(self):
        return f"Car(x={self.x}, v={self.v}, vmax={self.vmax}, a={self.a}, l={self.length}, tr={self.reaction_time}, vd={self.desired_velocity}, fc={self.f_car}, bc={self.b_car})"

    def __repr__(self):
        return f"Car(x={self.x}, v={self.v}, vmax={self.vmax}, a={self.a}, l={self.length}, tr={self.reaction_time}, vd={self.desired_velocity}, fc={self.f_car}, bc={self.b_car})"

    def check_crash(self):
        if self.distance_to_front_car():
            if self.distance_to_front_car() <= 0:
                print("Crash!")
                self.crashed = True

    def check_rear_end(self):
        if self.distance_to_front_car():
            if self.distance_to_back_car() <= 0:
                print("Rear end!")
                self.crashed = True

    def collides(self):
        return self.crashed

    def accelerate(self):
        if self.v < self.vmax:
            self.v = self.v + self.a
        else:
            self.v = self.vmax

        if self.v < 0:
            self.v = 0

        # if self.b_car is not None:
        #     if self.b_car.x - self.x < self.v:
        #         self.v = self.b_car.x - self.x

    def decelerate(self):
        if self.f_car is not None:
            if self.f_car.x - self.x < self.v:
                self.v = self.f_car.x - self.x

    def keep_velocity(self):
        pass

    def distance_to_front_car(self):
        if self.f_car is not None:
            return self.f_car.x - self.x
        else:
            return None

    def distance_to_back_car(self):
        if self.bc is not None:
            return self.x - self.bc.x
        else:
            return None

    def move(self):
        self.x = self.x + self.v

    def get_position(self):
        return self.x

    def custom_behavior(self):
        # if self.x > 300 and self.x < 1000:
        #    self.v = 40

        # random behavior
        if randint(0, 100) < 5:
            if self.v > 0:
                self.a = randint(0, self.a + 4)
            else:
                self.v += randint(0, 10)

    def dead_stop(self):
        if self.v > 0:
            if self.v > 10:
                self.v -= 10
            else:
                self.v = 0

    def update(self):

        if not self.crashed:
            self.check_crash()

            self.custom_behavior()
            self.accelerate()
            self.decelerate()
            self.keep_velocity()
            self.move()

        else:
            self.dead_stop()

        self.t += 1
