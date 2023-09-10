import gc
from typing import Callable
import numpy as np
from car import Car


class Highway:
    def __init__(self, length: float, crash_remove_delay: int = 5000, precision: int = 1):
        self.length = length
        self.cars = []
        self.time = 0

        self.crashes = []
        self.crash_remove_delay = crash_remove_delay
        self.historic_ids = []

        self.historic_velocities = []
        self.historic_accelerations = []
        self.historic_trip_duration = []

        self.historic_crash_count = 0

        self.precision = precision

    def __len__(self):
        return len(self.cars)

    def get_crash_count(self):
        return self.historic_crash_count

    def get_avg_v(self):
        if len(self.historic_velocities) == 0:
            return 0
        return np.mean(self.historic_velocities)

    def get_avg_a(self):
        if len(self.historic_accelerations) == 0:
            return 0
        return np.mean(self.historic_accelerations)

    def get_avg_trip_duration(self):
        if len(self.historic_trip_duration) == 0:
            return 0
        return np.mean(self.historic_trip_duration)

    def get_max_v(self):
        if (len(self.historic_velocities)) == 0:
            return 0
        return np.max(self.historic_velocities)

    def get_max_a(self):
        if (len(self.historic_accelerations)) == 0:
            return 0
        return np.max(self.historic_accelerations)

    def get_max_trip_duration(self):
        if (len(self.historic_trip_duration)) == 0:
            return 0
        return np.max(self.historic_trip_duration)

    def get_min_v(self):
        if (len(self.historic_velocities)) == 0:
            return 0
        return np.min(self.historic_velocities)

    def get_min_a(self):
        if (len(self.historic_accelerations)) == 0:
            return 0
        return np.min(self.historic_accelerations)

    def get_min_trip_duration(self):
        if (len(self.historic_trip_duration)) == 0:
            return 0
        return np.min(self.historic_trip_duration)

    def __str__(self):
        return (
            f"Highway(length={self.length}, cars=[\n"
            + "\n".join([f"\t{car}" for car in self.cars])
            + "\n])"
        )

    def __repr__(self):
        return (
            f"Highway(length={self.length}, cars=[\n"
            + "\n".join([f"\t{car}" for car in self.cars])
            + "\n])"
        )

    def get_front_car(self):
        if len(self.cars) == 0:
            return None
        return self.cars[-1]

    def get_back_car(self):
        if len(self.cars) == 0:
            return None
        return self.cars[0]

    def add_car(self, car: Car):

        car.set_precision(self.precision)

        if not car.id:
            car.id = len(self.historic_ids)
            self.historic_ids.append(car.id)
        if car.id and car.id not in self.historic_ids:
            self.historic_ids.append(car.id)

        if car.get_position() is None:
            car.x = 0
            self.cars = [car] + self.cars

            if len(self.cars) > 1:
                self.cars[1].b_car = car
                self.cars[0].f_car = self.cars[1]
            return

        if car.get_position() == 0:
            if len(self.cars) > 0:
                self.cars[0].b_car = car
                car.f_car = self.cars[0]
            self.cars = [car] + self.cars
            return

        if car.get_position() > self.length:
            # raise ValueError("Car position is greater than highway length")
            return

        if len(self.cars) > 0:
            car.b_car = self.cars[-1]
            self.cars[-1].f_car = car

        self.cars.append(car)

        car.set_highway(self)

    def remove_car(self, car: Car):
        if car in self.cars:
            # Remove references to car
            if car.f_car:
                car.f_car.b_car = car.b_car
            if car.b_car:
                car.b_car.f_car = car.f_car

            self.cars.remove(car)

            del car
            gc.collect()

    def tow_cars(self, now: bool = False):
        for car, frame in self.crashes:
            if now or frame + self.crash_remove_delay == self.time:
                print(f"AGP: Towing car {car.id} from {car.x} at frame {self.time}")
                self.remove_car(car)
                self.crashes.remove((car, frame))
                self.historic_crash_count += 1

    def update(self, frame: int, exit_logger: Callable, crash_logger: Callable):
        for car in self.cars:
            car.update(frame)

            self.historic_velocities.append(car.v)
            self.historic_accelerations.append(car.a)

            if car.crashed:
                if car not in [c for c, _ in self.crashes]:
                    print(f"AGP: Car {car.id} crashed at frame {frame}, queueing tow")
                    crash_logger(car, frame)
                    self.crashes.append((car, frame))

            if self.has_crashes():
                self.tow_cars()

            if car.get_position() > self.length:
                self.historic_trip_duration.append(car.time_ellapsed)
                exit_logger(car, frame)
                self.remove_car(car)

            if len(self.cars) > 0:
                self.cars[-1].f_car = None

        if len(self.cars) == 0:
            return 2

        self.time += 1

        return 1

    def has_crashes(self) -> bool:
        return len(self.crashes) > 0

    def run(self, time: float):
        pass

    def measure(self):
        pass

    def plot(self):
        pass

    def get_cars(self):
        return self.cars

    def get_cars_positions(self):
        return [car.get_position() for car in self.cars]

    def get_cars_velocities(self):
        return [car.v for car in self.cars]

    def get_cars_accelerations(self):
        return [car.a for car in self.cars]

    def get_cars_distances(self):
        pass

    def get_cars_times(self):
        return [car.time_ellapsed for car in self.cars]

    def get_cars_reaction_times(self):
        pass

    def get_cars_desired_velocities(self):
        pass

    def get_cars_front_cars(self):
        pass

    def get_cars_back_cars(self):
        pass
