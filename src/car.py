from typing import Optional

import numpy as np


class Car:
    def __init__(
        self,
        x: float,
        v: float,
        vmax: float,
        a: float,
        amax: float,
        length: float,
        tr: float,
        vd: float,
        bc: "Car",
        fc: Optional["Car"] = None,
        will_measure: Optional[bool] = False,
        init_frame: Optional[int] = None,
        car_id: Optional[int] = None,
    ):
        self.id = np.random.randint(0, 1000000) if car_id is None else car_id

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
        self.amax = amax

        self.throttle_acc = 0.1
        self.stopping_acc = 0.5

        self.length = length

        self.reaction_time = tr
        self.desired_velocity = vd

        self.f_car = fc
        self.b_car = bc

        self.will_measure = will_measure

        self.crashed = False

        self.init_frame = init_frame

        self.action_queue = []

    def __str__(self):
        return f"Car(x={self.x}, v={self.v}, vmax={self.vmax}, a={self.a}, l={self.length}, tr={self.reaction_time}, vd={self.desired_velocity}, fc={self.f_car}, bc={self.b_car})"

    def __repr__(self):
        return f"Car(x={self.x}, v={self.v}, vmax={self.vmax}, a={self.a}, l={self.length}, tr={self.reaction_time}, vd={self.desired_velocity}, fc={self.f_car}, bc={self.b_car})"

    def check_crash(self):
        if (
            not self.crashed
            and self.distance_to_front_car()
            and self.distance_to_front_car() <= 0
        ):
            print(
                f"Car {self.id} crashed at frame {self.t} in position {self.x} to car {self.f_car.id}"
            )
            self.crashed = True

    def check_rear_end(self):
        if (
            not self.crashed
            and self.distance_to_back_car()
            and self.distance_to_back_car() <= 0
        ):
            print(f"Car {self.id} rear-ended at frame {self.t} in position {self.x}")
            self.crashed = True

    def collides(self):
        return self.crashed

    def accelerate(self):
        if self.a < 0:
            self.a = 0
        self.a += self.throttle_acc
        if self.a > self.amax:
            self.a = self.amax

    def decelerate(self):
        self.a -= self.throttle_acc

    def stop(self):
        # self.a = -self.stopping_acc * self.v
        self.a = 0
        self.v = 0

    def keep_velocity(self):
        pass

    def distance_to_front_car(self) -> Optional[float]:
        """Calculates the distance to the front car


        Returns:
            float: Front Car X - Car X
        """
        if self.f_car is not None:
            return self.f_car.x - self.x
        else:
            return None

    def distance_to_back_car(self) -> Optional[float]:
        """Calculates the distance to the back car


        Returns:
            float: Car X - Back Car X
        """
        if self.b_car is not None:
            return self.x - self.b_car.x
        else:
            return None

    def get_position(self):
        return self.x

    def custom_behavior(self):
        pass

    def dead_stop(self):
        self.v = 0
        self.a = 0

    def set_initial_frame(self, frame: int):
        self.init_frame = frame

    def get_initial_frame(self):
        return self.init_frame

    def update(self, frame: int):

        self.check_crash()
        self.check_rear_end()

        if self.collides():
            self.dead_stop()
            self.action_queue = []

        else:
            # Update position
            self.x = self.x + self.v * 0.01

            # Update velocity
            self.v = self.v + self.a * 0.01

            if self.v > self.vmax:
                self.v = self.vmax

            if self.v < 0:
                self.v = 0

            # Decision making

            # Queue actions to be taken in (frame + reaction_time)
            # Crashing does not take into account reaction time

            # With a ceartain probability, the car will stop


            if self.v < self.desired_velocity:
                if self.f_car is not None:

                    # If front car has crashed, stop
                    if self.f_car.collides():
                        self.action_queue.append(
                            (self.stop, frame + self.reaction_time)
                        )

                    elif self.distance_to_front_car() <= self.v:

                        self.action_queue.append(
                            (self.stop, frame + self.reaction_time)
                        )
                    elif self.distance_to_front_car() <= 2 * self.v:
                        # LEQ Two seconds of distance: Decelerate
                        self.action_queue.append(
                            (self.decelerate, frame + self.reaction_time)
                        )
                    else:
                        self.action_queue.append(
                            (self.accelerate, frame + self.reaction_time)
                        )
            else:
                self.action_queue.append(
                    (self.keep_velocity, frame + self.reaction_time)
                )

            # Take actions
            for action, action_frame in self.action_queue:
                if frame <= action_frame:
                    action()

            # Remove actions that have been taken
            self.action_queue = [
                action for action in self.action_queue if action[1] >= frame
            ]

        self.t += 1
