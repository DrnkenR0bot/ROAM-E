import sys
import time
import board
import pwmio
import adafruit_hcsr04
from adafruit_motor import servo
from note_frequencies import cMaj_scale
from motor_dr import Motor, Loco

#
# Component initialization
#

# Initialize piezo buzzer
piezo = pwmio.PWMOut(board.GP22, variable_frequency=True)

# Initialize sonar
sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.GP28, echo_pin=board.GP7)
cliff_sensor = adafruit_hcsr04.HCSR04(trigger_pin=board.GP1, echo_pin=board.GP0)

# Initialize neck servos
pa = pwmio.PWMOut(board.GP12, duty_cycle=2**15, frequency=100)
pb = pwmio.PWMOut(board.GP13, duty_cycle=2**15, frequency=100)
sa = servo.Servo(pa)
sb = servo.Servo(pb)
sa.angle = 90
sb.angle = 90

# Initialize left and right motors
left_motor = Motor(board.GP10, board.GP11, down_calibrate=1.0)
right_motor = Motor(board.GP8, board.GP9, down_calibrate=1.0)

# Initialize Loco(motion) control
loco = Loco(left_motor, right_motor)
loco.stop()


#
# Function definitions
#

def beep(frequency, buzzer=piezo, duration: float = 0.5, volume_exponent: int = 11):
    if volume_exponent > 15:
        ON = 2**15
    else:
        ON = 2**volume_exponent
    OFF = 0
    buzzer.frequency = int(frequency)
    buzzer.duty_cycle = ON
    time.sleep(duration)
    buzzer.duty_cycle = OFF

def distance(cm2xscale: float = 1.):
    """
    Return sonar distance to object.
    
    :param cm2xscale: Use to scale from native cm to any units. Default is meters (1e-2).
    """
    return sonar.distance*cm2xscale

def statistical_distance(
        cm2xscale: float = 1., 
        samples: int = 10, 
        sample_interval: float = 0.01,
        print_distance: bool = False
        ):
    d = []
    for i in range(samples):
        d.append(distance(cm2xscale=cm2xscale))
        time.sleep(sample_interval)
    result = sum(d)/samples
    if print_distance:
        print(f"Statistical distance = {result}")
    return result

def neck(angle, pause_time: float = 2.):
    sa.angle = angle
    time.sleep(pause_time)
    return angle

def head(angle, pause_time: float = 0.2):
    sb.angle = angle
    time.sleep(pause_time)
    return angle

def scan_horizon():
    data = []
    head(90)
    for angle in range(0, 180, 5):
        head(angle)
        data.append((angle, statistical_distance()))
        print(f"(angle, distance) = {data[-1]}")
        print(cliff_sensor.distance)
    head(90)
    return data

def find_max_distance(data):
    max_distance = 0.
    for angle, distance in data:
        if distance > max_distance:
            max_distance = distance
            max_distance_angle = angle
    return (max_distance_angle, max_distance)

class CliffError(Exception):
    """Error to be raised when a cliff is detected. Allows function interrupt."""
    pass

def cliff_detect(ground_distance:float = 15., delta:float = 5., sleep_delay:float = 0.1) -> None:
    if cliff_sensor.distance >= (ground_distance + delta):
        raise CliffError
    # Give cliff_sensor some breathing room to avoid comm errors.
    time.sleep(sleep_delay)

def cliff_response(ground_distance = 15.) -> bool:
    loco.stop()
    head(90.)
    neck(10.)
    data = scan_horizon()
    (_, max_distance) = find_max_distance(data)
    neck(90., pause_time=0.1)
    if max_distance >= ground_distance:
        print("CLIFF CONFIRMED! Avoiding.")
        loco.backward()
        time.sleep(3)
        loco.right_spin()
        time.sleep(3)
        return True
    else:
        print("Upon closer inspection, there is no cliff. Continuing.")
        return False

def match_range(
        angle, 
        distance, 
        tolerance: float = 10., 
        speed: float = 0.5, 
        spin_time: float = 20.
        ):
    def range(measurement, distance, tolerance):
        if measurement-tolerance >= distance <= measurement+tolerance:
            print(measurement + tolerance)
            print(measurement - tolerance)
            return True
        else:
            return False
    def check_distance(distance, tolerance):
        if cliff_detect():
            raise CliffError
        if range(statistical_distance(print_distance=False), distance, tolerance):
            loco.stop()
            return True
        if time.monotonic() >= start_time + spin_time:
            print("Proper distance not found!!!")
            return False
        return None
    # Begin actual function
    try:
        start_time = time.monotonic()
        if angle == 90.:
            return True
        elif angle > 90.:
            loco.left_spin(speed = speed)
            print(f"Angle = {angle}, turning left.")
        elif angle < 90.:
            print(f"Angle = {angle}, turning right.")
            loco.right_spin(speed = speed)
        while True:
            status = check_distance(distance, tolerance)
            if status is not None:
                loco.stop()
                print(f"Found = {status}")
                return status
    except CliffError:
        return cliff_response()

def find_path():
    data = scan_horizon()
    driving_direction = find_max_distance(data)
    print(f"Max distance bearing: {driving_direction}")
    bearing_identified = match_range(*driving_direction)
    if bearing_identified:
        return True
    else:
        loco.stop()
        print("I DON'T KNOW WHAT TO DO!!!")
        return False

def drive(forward_speed: float = 1., wall_distance: float = 30., scan_interval: float = 0.5):
    loco.forward(speed=forward_speed)
    start_time = 0.
    try:
        while True:
            cliff_detect()
            if time.monotonic() >= start_time + scan_interval:
                if statistical_distance() <= wall_distance:
                    loco.stop()
                    # throw in an emotional response here
                    break
                else:
                    start_time = time.monotonic()
    except CliffError:
        cliff_response()

#
# Main
#
if __name__ == "__main__":

    # Power up buzzer tones
    for key, tone in cMaj_scale.items():
        if key[0] == "G":
            beep(tone, duration=0.1)

    # Begin roaming loop
    keep_looping = True
    while keep_looping:
        drive(forward_speed=0.8)
        keep_looping = find_path()

    # Program fail tones
    beep(cMaj_scale["E3"], duration=1.)
    beep(cMaj_scale["D3"], duration=1.)
    beep(cMaj_scale["C3"], duration=2.)
