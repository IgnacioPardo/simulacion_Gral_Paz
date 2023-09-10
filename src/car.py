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

        self.time_ellapsed = 0

        # Internally, we use SI units
        # Position in meters
        # Velocity in m/s
        # Acceleration is in m/s^2

        # Externally, we use km/h for velocity
        # But we convert it to m/s internally

        self.x = x

        self.v = v / 3.6
        self.vmax = vmax / 3.6
        vd = vd / 3.6
        self.desired_velocity = vd if vd < self.vmax else self.vmax

        self.a = a
        self.amax = amax

        self.throttle_acc = 0.1
        self.stopping_acc = 0.3

        self.length = length

        self.reaction_time = tr

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

        self.posible_actions = [
            self.accelerate,
            self.decelerate,
            self.stop,
            self.keep_velocity,
        ]

        self.historic_velocities = []
        self.historic_accelerations = []

    def __str__(self):
        return f"Car(x={self.x}, v={self.v}, vmax={self.vmax}, a={self.a}, l={self.length}, tr={self.get_reaction_time()}, vd={self.desired_velocity}, fc={self.f_car.id}, bc={self.b_car.id})"

    def __repr__(self):
        return f"Car(x={self.x}, v={self.v}, vmax={self.vmax}, a={self.a}, l={self.length}, tr={self.get_reaction_time()}, vd={self.desired_velocity}, fc={self.f_car.id}, bc={self.b_car.id})"

    def __eq__(self, other):
        return self.id == other.id

    def check_frontal_crash(self):
        if (
            not self.crashed
            and self.distance_to_front_car()
            and self.distance_to_front_car() <= 0
        ):
            print(
                f"Car {self.id} crashed at frame {self.time_ellapsed} in position {self.x} to car {self.f_car.id}"
            )
            self.crashed = True

    def check_rear_end(self):
        if (
            not self.crashed
            and self.distance_to_back_car()
            and self.distance_to_back_car() <= 0
        ):
            print(
                f"Car {self.id} rear-ended at frame {self.time_ellapsed} in position {self.x}"
            )
            self.crashed = True

    def has_collided(self):
        self.check_frontal_crash()
        self.check_rear_end()
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

    def get_velocity(self):
        return self.v

    def dead_stop(self):
        self.v = 0
        self.a = 0

    def set_initial_frame(self, frame: int):
        self.init_frame = frame

    def get_initial_frame(self):
        return self.init_frame

    def set_highway(self, highway):
        self.highway = highway

    def physics(self):
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

    def update(self, frame: int):

        self.physics()

        if self.has_collided():
            self.action_queue = list(
                filter(lambda x: x[0] == self.stop, self.action_queue)
            )
            self.action_queue.append((self.decelerate, frame))
        else:

            self.historic_velocities.append(self.v)
            self.historic_accelerations.append(self.a)

            # Decision making

            # Queue actions to be taken in (frame + reaction_time)
            # Crashing does not take into account reaction time, its immediate

            self.custom_behavior(frame)
            self.slugish_behavior(frame)
            self.sleepy_behavior(frame)

            self.behaviour(frame)

        # Resolve actions in the current frame
        self.resolve_actions(frame)

        self.time_ellapsed += 1

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

    def slugish_behavior(self, frame):
        if self.v < 0.1:
            self.action_queue.append(
                (self.accelerate, frame + self.get_reaction_time())
            )

    def sleepy_behavior(self, frame):
        # if acceleration didnt change much in the last updates
        # enter Decresed Attention mode

        if len(self.historic_accelerations) > 10:
            if (
                np.std(self.historic_accelerations[-10:]) < 0.1
                and not self.increased_attention
                and np.random.uniform() < 0.1
            ):
                self.decresed_attention = True
            else:
                self.decresed_attention = False

        if len(self.historic_velocities) > 10:
            if (
                np.std(self.historic_velocities[-10:]) < 0.1
                and not self.increased_attention
                and np.random.uniform() < 0.1
            ):
                self.decresed_attention = True
            else:
                self.decresed_attention = False

    def custom_behavior(self, frame):
        low = np.random.uniform(1000, 9000)
        high = np.random.uniform(low, 10000)
        if self.x < low and self.x > high:
            if np.random.uniform() < 0.01:
                # self.crashed = True
                self.v = self.vmax
                self.stopping_acc = 0
            if np.random.poisson(40) == 1:
                for _ in range(100):
                    self.action_queue.append(
                        (self.accelerate, frame + self.get_reaction_time())
                    )
                self.action_queue.append((self.stop, frame + self.get_reaction_time()))

        if (
            self.highway
            and self.highway.get_crash_count() == 0
            and frame > 3000
            and len(self.highway.historic_ids) > 100
        ):
            self.action_queue.append((self.stop, frame + self.get_reaction_time()))
            self.crashed = True
            self.highway.historic_crash_count += 1

        if np.random.uniform() < 0.6:
            self.decresed_attention = True

        if self.decresed_attention and np.random.uniform() < 0.1:
            self.decresed_attention = False

    def behaviour(self, frame):

        # If there are cars in front of me, I will slow down
        if self.crashes_upfront():
            if not self.increased_attention:
                self.action_queue.append((self.increase_attention, frame + 1))
        else:
            if self.increased_attention:
                self.action_queue.append((self.default_attention, frame + 1))

        # If the front car seems to be decelerating, I will decelerate
        # A car should not know exactly the acceleration of the front car
        if self.f_car is not None and self.f_car.a < np.random.normal(
            0, 0.1 - 0.05 * self.increased_attention + 0.5 * self.decresed_attention
        ):
            self.action_queue.append(
                (self.decelerate, frame + self.get_reaction_time())
            )

        if not self.stopping:
            should_acc = True

            if self.f_car is not None:
                if self.f_car.has_collided() or self.f_car.stopping:
                    should_acc = False
                    if self.distance_to_front_car() <= 8 * self.v:
                        self.action_queue.append(
                            (self.stop, frame + self.get_reaction_time())
                        )
                        self.action_queue = list(
                            filter(lambda x: x[0] == self.stop, self.action_queue)
                        )
                elif self.distance_to_front_car() <= 2 * self.v:
                    # LEQ Two seconds of distance: Decelerate
                    should_acc = False
                    self.action_queue.append(
                        (self.decelerate, frame + self.get_reaction_time())
                    )
                elif (
                    self.v
                    < self.f_car.v
                    + np.random.uniform(
                        0,
                        5 - 2 * self.increased_attention + 2 * self.decresed_attention,
                    )
                    and self.v < self.desired_velocity
                ):
                    # Same as the acceleration of the front car
                    # A car should not know exactly the velocity of the front car
                    # Error factor as to simulate an approximation
                    should_acc = False
                    self.action_queue.append(
                        (self.accelerate, frame + self.get_reaction_time())
                    )

            if self.v < self.desired_velocity and should_acc:
                self.action_queue.append(
                    (self.accelerate, frame + self.get_reaction_time())
                )
