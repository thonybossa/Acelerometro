import time
import board
import busio
import adafruit_adxl34x

# Inicializar el bus I2C y el sensor ADXL345
i2c = busio.I2C(board.SCL, board.SDA)
accelerometer = adafruit_adxl34x.ADXL345(i2c)

while True:
    # Leer valores de aceleración en los ejes X, Y y Z
    x, y, z = accelerometer.acceleration

    # Imprimir los valores capturados
    print(f"Acelerómetro - Eje X: {x:.2f}, Eje Y: {y:.2f}, Eje Z: {z:.2f}")

    time.sleep(1)  # Esperar 1 segundo antes de tomar la siguiente lectura

