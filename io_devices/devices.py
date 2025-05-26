class Device:
    def __init__(self, name):
        self.name = name

    def read(self):
        print(f"Leyendo desde el dispositivo {self.name}")
        return 0

    def write(self, data):
        print(f"Escribiendo {data} en el dispositivo {self.name}")
