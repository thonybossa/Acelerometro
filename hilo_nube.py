import threading
import queue
import serial
import time
import board
import busio
import adafruit_adxl34x
import math
import requests

# Configuración inicial para ThingSpeak
write_key = "M938VWCNQUOS6XDM"  # Reemplaza con tu clave de escritura API
thingspeak_url = "https://api.thingspeak.com/update"

# Configuración inicial del puerto serial y acelerómetro
serial_port = '/dev/ttyS0'
baud_rate = 115200
NUM_SAMPLES = 149  # Basado en una tasa de muestreo de aproximadamente 9.9 Hz

# Cola para compartir datos entre hilos
data_queue = queue.Queue()
command_queue = queue.Queue()

# Inicializar el bus I2C y el sensor ADXL345
i2c = busio.I2C(board.SCL, board.SDA)
accelerometer = adafruit_adxl34x.ADXL345(i2c)

# Inicialización del puerto serial
ser = serial.Serial(serial_port, baud_rate)

def read_accelerometer():
    while True:
        x, y, z = accelerometer.acceleration
        magnitude = math.sqrt(x**2 + y**2 + z**2)
        data_queue.put(magnitude)
        # time.sleep(0.01)  # Ajustar según la tasa de muestreo del sensor

def write_serial():
    global NUM_SAMPLES
    while True:
        if not command_queue.empty():
            NUM_SAMPLES = command_queue.get()
            while not data_queue.empty():
                data_queue.get()

        if data_queue.qsize() >= NUM_SAMPLES:
            data = [data_queue.get() for _ in range(NUM_SAMPLES)]
            avg = sum(data) / NUM_SAMPLES
            print(f"Valor del promedio enviado: {avg:.15f}")

            try:
                payload = {'api_key': write_key, 'field1': avg}
                response = requests.get(thingspeak_url, params=payload)
                print("Datos enviados a ThingSpeak:", response.text)
            except Exception as e:
                print("Error al enviar datos a ThingSpeak:", e)

            #time.sleep(15)  # Esperar 15 segundos antes de la próxima publicación

def read_serial():
    while True:
        line = ser.readline().decode().strip()
        print(f"Datos recibidos: {line}")

        commands = line.split("##")
        for cmd in commands:
            if cmd.startswith("PROMEDIO-") and cmd.endswith("-"):
                try:
                    num_str = cmd.replace("PROMEDIO-", "").replace("-", "")
                    num = int(num_str)
                    command_queue.put(num)
                    print(f"Comando válido recibido: Número de muestras cambiado a {num}")
                except ValueError:
                    print("Comando no válido")

# Crear y comenzar hilos
thread1 = threading.Thread(target=read_accelerometer)
thread2 = threading.Thread(target=write_serial)
thread3 = threading.Thread(target=read_serial)

thread1.start()
thread2.start()
thread3.start()