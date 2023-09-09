from typing import Optional

import numpy as np

PRECISION = 100


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
        self.vmax = vmax / 3.6

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

        self.highway = None

        self.increased_attention = False
        self.decresed_attention = False

        self.stopping = False

    def __str__(self):
        return f"Car(x={self.x}, v={self.v}, vmax={self.vmax}, a={self.a}, l={self.length}, tr={self.get_reaction_time()}, vd={self.desired_velocity}, fc={self.f_car.id}, bc={self.b_car.id})"

    def __repr__(self):
        return f"Car(x={self.x}, v={self.v}, vmax={self.vmax}, a={self.a}, l={self.length}, tr={self.get_reaction_time()}, vd={self.desired_velocity}, fc={self.f_car.id}, bc={self.b_car.id})"

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

    def has_collided(self):
        return self.crashed

    def accelerate(self):
        if self.a < 0:
            self.a = 0
        self.a += self.throttle_acc
        if self.a > self.amax:
            self.a = self.amax

    def decelerate(self):
        self.a -= self.stopping_acc / 5
        if self.a < -4:
            self.a = -4

    def stop(self):
        self.stopping = True

    def keep_velocity(self):
        pass

    def distance_to_front_car(self) -> Optional[float]:
        """Calculates the distance to the front car


        Returns:
            float: Front Car X - Car X
        """
        if self.f_car is not None:
            return self.f_car.x - (self.x + self.length)
        else:
            return None

    def distance_to_back_car(self) -> Optional[float]:
        """Calculates the distance to the back car


        Returns:
            float: Car X - Back Car X
        """
        if self.b_car is not None:
            return self.x - (self.b_car.x + self.b_car.length)
        else:
            return None

    def get_position(self):
        return self.x

    def dead_stop(self):
        self.v = 0
        self.a = 0

    def set_initial_frame(self, frame: int):
        self.init_frame = frame

    def get_initial_frame(self):
        return self.init_frame

    def set_highway(self, highway):
        self.highway = highway

    def update(self, frame: int):

        self.check_crash()
        self.check_rear_end()

        if self.has_collided():
            self.dead_stop()
            self.action_queue = []

        else:

            # Update position
            self.x = self.x + self.v / PRECISION

            # Update velocity
            self.v = self.v + self.a / PRECISION

            if self.stopping:
                self.v -= self.stopping_acc

            if self.v > self.vmax:
                self.v = self.vmax

            self.v = max(0, self.v)

            if self.v == 0:
                self.stopping = False
            # Decision making

            # Queue actions to be taken in (frame + reaction_time)
            # Crashing does not take into account reaction time, its immediate

            self.custom_behavior(frame)

            self.behaviour(frame)

            # Resolve actions in the current frame
            self.resolve_actions(frame)

        self.t += 1

    def resolve_actions(self, frame):
        for action, action_frame in self.action_queue:
            # print(f"Car {self.id} took action {action.__name__} at frame {frame}")
            if frame <= action_frame:
                p = np.random.uniform()
                if p < 0.1:
                    for _ in range(100):
                        action()
                if p < 0.07:
                    action()

        # Remove actions that have been taken
        self.action_queue = [
            action_pair for action_pair in self.action_queue if action_pair[1] >= frame
        ]

    def increase_attention(self):
        self.increased_attention = True

    def default_attention(self):
        self.increased_attention = False
        self.decresed_attention = False

    def get_reaction_time(self):
        if self.increased_attention:
            return self.reaction_time / 2
        elif self.decresed_attention:
            return self.reaction_time * 1.8
        return self.reaction_time

    def crashes_upfront(self):
        if self.highway:
            for car in self.highway.get_cars():
                if car != self and car.x > self.x and car.has_collided():
                    return True
        return False

    def __eq__(self, other):
        return self.id == other.id

    def custom_behavior(self, frame):
        if self.x > 4000 and self.x < 9000:
            if np.random.poisson(40) == 1:
                # self.crashed = True
                self.v = self.vmax
                self.stopping_acc = 0
            if np.random.poisson(40) == 1:
                for _ in range(100):
                    self.action_queue.append(
                        (self.accelerate, frame + self.get_reaction_time())
                    )
                self.action_queue.append(
                    (self.stop, frame + self.get_reaction_time() + 10)
                )

        if np.random.uniform() < 0.5:
            self.decresed_attention = True

        if self.decresed_attention and np.random.uniform() < 0.3:
            self.decresed_attention = False

    def behaviour(self, frame):

        # If there are cars in front of me, I will slow down
        if self.crashes_upfront():
            if not self.increased_attention:
                self.action_queue.append((self.increase_attention, frame + 1))

            # if self.v > 0:
            #     self.action_queue.append(
            #         (self.decelerate, frame + self.get_reaction_time())
            #     )
        else:
            if self.increased_attention:
                self.action_queue.append((self.default_attention, frame + 1))

        if self.f_car is not None and self.f_car.a < 0 and self.v > 0:
            # If the front car is braking, I will brake
            # self.action_queue.append(
            # (self.decelerate, frame + self.get_reaction_time())
            # )
            None

        if self.f_car is not None:
            if self.v < self.desired_velocity:
                # If front car has crashed, stop
                if self.f_car.has_collided():
                    self.action_queue.append(
                        (self.stop, frame + self.get_reaction_time())
                    )

                    # self.action_queue.append(
                    # (self.decelerate, frame + self.get_reaction_time())
                    # )
                elif self.distance_to_front_car() <= 5 * self.v:
                    # LEQ Two seconds of distance: Decelerate
                    self.action_queue.append(
                        (self.decelerate, frame + self.get_reaction_time())
                    )
                elif self.v < self.f_car.v:
                    self.action_queue.append(
                        (self.accelerate, frame + self.get_reaction_time())
                    )
            else:
                # If front car has crashed, stop
                if self.f_car.has_collided():
                    if self.distance_to_front_car() <= 0.5 * self.v:
                        self.action_queue.append(
                            (self.decelerate, frame + self.get_reaction_time())
                        )
                    else:
                        self.action_queue.append(
                            (self.keep_velocity, frame + self.get_reaction_time())
                        )

                elif self.distance_to_front_car() <= 5 * self.v:
                    # LEQ Two seconds of distance: Decelerate
                    self.action_queue.append(
                        (self.decelerate, frame + self.get_reaction_time())
                    )
        else:
            if self.v < self.desired_velocity:
                self.action_queue.append(
                    (self.accelerate, frame + self.get_reaction_time())
                )
