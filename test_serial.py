import serial
import time

PORT = "/dev/cu.usbmodem11401"
BAUDRATE = 115200

print(f"Tentando abrir {PORT}...")

try:
    ser = serial.Serial(PORT, BAUDRATE, timeout=1)
    print("Porta aberta com sucesso!")
    print("Lendo dados (pressione Ctrl+C para sair)...")
    
    while True:
        if ser.in_waiting > 0:
            line = ser.readline()
            try:
                decoded = line.decode('utf-8').strip()
                print(f"Recebido: {decoded}")
            except Exception as e:
                print(f"Erro ao decodificar: {e}")
        time.sleep(0.1)

except serial.SerialException as e:
    print(f"Erro serial: {e}")
except KeyboardInterrupt:
    print("\nEncerrando...")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Porta fechada.")
