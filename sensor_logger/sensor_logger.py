import struct
import serial
from io import BytesIO
import signal
import sys
import csv
from datetime import datetime, timedelta

HEADER_MAGIC = b'QXO_STLE'
FOOTER_MAGIC = b'END_DATA'

usb_serial = None

def readstruct(s, f):
    return struct.unpack(s, f.read(struct.calcsize(s)))

def _parse_sensor(data):
    return struct.unpack('<hhh', data)

def parse_dataset(dataset):
    f = BytesIO(dataset)
    magic, version, headersize, bodysize, sensorcount, curtick = readstruct('<8sIIIII', f)
    sensors = []
    for _ in range(sensorcount):
        sensors.append(readstruct('<II', f))

    sensordata = {}
    for sid, size in sensors:
        sdata = f.read(size)
        if len(sdata) != size:
            return curtick, None
        if sid == 1:
            sensordata['accel'] = _parse_sensor(sdata[:6])
        elif sid == 2:
            sensordata['gyro'] = _parse_sensor(sdata[:6])
    return curtick, sensordata

def packing_dataset(data_buffer, data):
    if data:
        data_buffer += data

    while True:
        idx_header = data_buffer.find(HEADER_MAGIC)
        if idx_header < 0:
            data_buffer.clear()
            return None
        if idx_header > 0:
            del data_buffer[:idx_header]

        idx_footer = data_buffer.find(FOOTER_MAGIC, len(HEADER_MAGIC))
        if idx_footer < 0:
            return None

        idx_footer += len(FOOTER_MAGIC)
        packet = data_buffer[:idx_footer]
        del data_buffer[:idx_footer]
        return packet

def sig_handler(sig, frame):
    global usb_serial
    if usb_serial:
        usb_serial.close()
    print("🔌 Serial closed.")
    sys.exit(0)

def main():
    global usb_serial
    usb_serial = serial.Serial('COM29', 1500000, timeout=1)

    # ✅ 加入設定 buffer 大小
    usb_serial.set_buffer_size(rx_size=300000, tx_size=128)

    usb_serial.reset_input_buffer()
    data_buffer = bytearray()

    filename = datetime.now().strftime("sensor_speedtest_%Y%m%d_%H%M%S.csv")
    csv_file = open(filename, mode='w', newline='')
    writer = csv.writer(csv_file)
    writer.writerow(['TS', 'AX', 'AY', 'AZ', 'GX', 'GY', 'GZ'])

    count = 0
    t_start = datetime.now()

    try:
        while True:
            data = usb_serial.read(usb_serial.in_waiting or 64)
            if data:
                data_buffer.extend(data)

            while True:
                packet = packing_dataset(data_buffer, b'')
                if not packet:
                    break
                ts, sensordata = parse_dataset(packet)
                if sensordata:
                    accel = sensordata.get('accel', (0, 0, 0))
                    gyro = sensordata.get('gyro', (0, 0, 0))
                    writer.writerow([ts, *accel, *gyro])
                    count += 1

            # 每秒顯示一次速率
            if (datetime.now() - t_start).total_seconds() >= 1.0:
                print(f"Samples/sec: {count}")
                count = 0
                t_start = datetime.now()

    except KeyboardInterrupt:
        print("✅ 停止記錄")
    except Exception as e:
        print(f"❌ 錯誤: {e}")
    finally:
        csv_file.close()
        usb_serial.close()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, sig_handler)
    main()
