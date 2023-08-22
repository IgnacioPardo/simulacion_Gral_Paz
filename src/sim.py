"""
# simulating a highway

- discrete event simulation
- our goal: to implement a realistic simulation of Avenida General Paz (AGP) from Liniers to Lugones
- we want to:
- quantify the statistics of travel times and their dependence on maximum legal speed, traffic density, average driver behavior, etc
- explore traffic shock waves
- introduce a realistic mechanism for infrequent collisions and recovery
- quantify the probability of an accident in the next ten minutes for a driver that is surrounded by high density traffic
- think how to improve welfare (tolls, broadcasting, fines, etc) model changing lanes. cars sharing the road with trucks. mix humans with self-driving cars
- anything else that you might find interesting and non trivial

## how do you drive?

- what information do you use when driving?
- what actions do you take when driving?
- what constraints do you face?
- how rapidly do you react when driving?

## agents in a highway

- what is a natural definition for an agent?
- what is a reasonable goal for an agent?
- what are the state variables that describe the state of an agent?
- what information is available to an agent?
- is there randomness in the behavior of an agent?

## the environment

- how can Avenida Gral Paz (AGP) be represented? dimensions for AGP?
- how many lanes?
- how do cars enter / exit AGP?

## coding the model

- how do we represent a collection of cars in AGP?
- how do we measure distance?
- what is the initial state of the highway?
- how do we represent the passage of time? reasonable clock?
- how do we represent the movement of cars?
- what is the quantitative outcome of our simulation?

## First idea

### Data Types

AGP is a Queue of Cars. So Single Lane.

Car has properties:

Each car has a position (x) and a velocity (v)s
and a maximum velocity (vmax).
maybe an acceleration (a) and a length (l) too.

Each car has a driver.
The driver has a reaction time (tr) and a desired velocity (vd).

Each car has a front car and a back car.
The front car is the one in front of it in the queue.
The back car is the one behind it in the queue.

Each car can calculate:
- its distance to the front car (df)
- its distance to the back car (db).

By asking the front car for its position and the back car for its position.

(If each car has a lenght take it into account when calculating df and db)

Also each car should know its elapsed time (t) since it entered the highway.

Car properties:
- position (x)
- velocity (v)
- maximum velocity (vmax)
- acceleration (a)
- length (l)
- reaction time (tr)
- desired velocity (vd)
- front car (fc)
- back car (bc)
- elapsed time (t)

### Behavior

A car can accelerate, decelerate, or keep its velocity.
Cars prefer not to crash into each other.

A car can accelerate if its velocity is less than its maximum velocity.

¿Can a car calculate how long would it take to reach the front car if it accelerates?

A car can maybe know also the velocity of the front car.

A car can decelerate if its distance to the front car is less than its velocity.

A car can keep its velocity if its distance to the front car is equal or greater than its velocity.

If its position is equal to the length of the highway, it can exit the highway.

"""

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

        self.t = 0

        self.x = x
        self.v = v
        self.vmax = vmax
        self.a = a
        self.length = l

        self.reaction_time = tr
        self.desired_velocity = vd

        self.f_car = fc
        self.b_car = bc

        self.will_measure = will_measure

    def __str__(self):
        return f"Car(x={self.x}, v={self.v}, vmax={self.vmax}, a={self.a}, l={self.l}, tr={self.tr}, vd={self.vd}, fc={self.fc}, bc={self.bc})"

    def __repr__(self):
        return f"Car(x={self.x}, v={self.v}, vmax={self.vmax}, a={self.a}, l={self.l}, tr={self.tr}, vd={self.vd}, fc={self.fc}, bc={self.bc})"

    def accelerate(self):
        if self.v < self.vmax:
            self.v = self.v + self.a
        else:
            self.v = self.vmax

    def decelerate(self):
        if self.fc is not None:
            if self.fc.x - self.x < self.v:
                self.v = self.fc.x - self.x

    def keep_velocity(self):
        pass

    def distance_to_front_car(self):
        if self.fc is not None:
            return self.fc.x - self.x
        else:
            return None

    def distance_to_back_car(self):
        if self.bc is not None:
            return self.x - self.bc.x
        else:
            return None

    def move(self):
        self.x = self.x + self.v

    def update(self):
        self.accelerate()
        self.decelerate()
        self.keep_velocity()
        self.move()


class Highway:
    def __init__(self, length: float):
        self.length = length
        self.cars = []
        self.time = 0

    def __str__(self):
        return f"Highway(length={self.length}, lanes={self.lanes}, cars={self.cars})"

    def __repr__(self):
        return f"Highway(length={self.length}, lanes={self.lanes}, cars={self.cars})"

    def add_car(self, car: Car):
        self.cars.append(car)

    def update(self):
        for car in self.cars:
            car.update()

    def run(self, time: float):
        pass

    def measure(self):
        pass

    def plot(self):
        pass

    def get_cars(self):
        pass

    def get_cars_positions(self):
        pass

    def get_cars_velocities(self):
        pass

    def get_cars_accelerations(self):
        pass

    def get_cars_distances(self):
        pass

    def get_cars_times(self):
        pass

    def get_cars_reaction_times(self):
        pass

    def get_cars_desired_velocities(self):
        pass

    def get_cars_front_cars(self):
        pass

    def get_cars_back_cars(self):
        pass
