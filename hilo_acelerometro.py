import threading
import queue
import serial
import time
import board
import busio
import adafruit_adxl34x
import math

# Configuración inicial
serial_port = '/dev/ttyS0'
baud_rate = 115200
NUM_SAMPLES = 10

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
        # Leer valores de aceleración
        x, y, z = accelerometer.acceleration
        # Calcular magnitud
        magnitude = math.sqrt(x**2 + y**2 + z**2)

        # Enviar a la cola
        data_queue.put(magnitude)
        #time.sleep(0.01)  # Ajustar según la tasa de muestreo del sensor

#def write_serial():
 #   global NUM_SAMPLES
  #  while True:
        # Esperar a tener suficientes datos
   #     if data_queue.qsize() >= NUM_SAMPLES:
    #        data = [data_queue.get() for _ in range(NUM_SAMPLES)]
     #       avg = sum(data) / NUM_SAMPLES
      #      ser.write(f"{avg:.2f}\n".encode())  # Enviar solo el número

       # time.sleep(1)

def write_serial():
    global NUM_SAMPLES
    while True:
        # Verificar si hay un nuevo comando y actualizar NUM_SAMPLES
        if not command_queue.empty():
            NUM_SAMPLES = command_queue.get()
            # Vaciar la cola de datos para empezar con las nuevas N muestras
            while not data_queue.empty():
                data_queue.get()

        # Esperar a tener suficientes datos
        if data_queue.qsize() >= NUM_SAMPLES:
            data = [data_queue.get() for _ in range(NUM_SAMPLES)]
            # Imprimir los valores utilizados para calcular el promedio
            print(f"Valores utilizados para el promedio ({NUM_SAMPLES} muestras): {data}")

            avg = sum(data) / NUM_SAMPLES
            print(f"Valor del promedio enviado: {avg:.2f}")
            ser.write(f"{avg:.2f}\n".encode())  # Enviar solo el número

        time.sleep(1)

def read_serial():
    while True:
        line = ser.readline().decode().strip()
        print(f"Datos recibidos: {line}")  # Mensaje de depuración

        # Separar múltiples comandos en la misma línea
        commands = line.split("##")
        for cmd in commands:
            if cmd.startswith("PROMEDIO-") and cmd.endswith("-"):
                try:
                    num_str = cmd.replace("PROMEDIO-", "").replace("-", "")
                    num = int(num_str)
                    command_queue.put(num)
                    print(f"Comando válido recibido: Número de muestras cambiado a {num}")  # Mensaje de depuración
                except ValueError:
                    print("Comando no válido")


# Crear y comenzar hilos
thread1 = threading.Thread(target=read_accelerometer)
thread2 = threading.Thread(target=write_serial)
thread3 = threading.Thread(target=read_serial)

thread1.start()
thread2.start()
thread3.start()