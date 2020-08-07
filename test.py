class Car:
    def __init__(self, id):
        self.id = id


cars = []
for i in range(1, 10):
    cars.append(Car(i))

# for car in cars:
#     print(car.id)

cars.remove(cars[4])

for i, car in enumerate(cars):
    if i == 4:
        cars.remove(car)


for i, car in enumerate(cars):
    print(i, car.id)
