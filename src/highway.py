from car import Car


class Highway:
    def __init__(self, length: float):
        self.length = length
        self.cars = []
        self.time = 0

        self.crashes = []
        self.crash_remove_delay = 5000
        self.historic_ids = []

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
            print(f"AGP: Removing car {car.id} from highway at frame {self.time}")
            # Remove references to car
            if car.f_car:
                car.f_car.b_car = car.b_car
            if car.b_car:
                car.b_car.f_car = car.f_car
            
            self.cars.remove(car)

    def tow_cars(self, now: bool = False):
        for car, frame in self.crashes:
            if now or frame + self.crash_remove_delay == self.time:
                self.remove_car(car)
                self.crashes.remove((car, frame))

    def update(self, frame: int):
        for car in self.cars:
            car.update(frame)

            if car.crashed:
                if car not in [c for c, _ in self.crashes]:
                    print(f"AGP: Car {car.id} crashed at frame {frame}, queueing tow")
                    self.crashes.append((car, frame))

            if self.has_crashes():
                self.tow_cars()

            if car.get_position() > self.length:
                self.cars.remove(car)

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
        return [car.t for car in self.cars]

    def get_cars_reaction_times(self):
        pass

    def get_cars_desired_velocities(self):
        pass

    def get_cars_front_cars(self):
        pass

    def get_cars_back_cars(self):
        pass
