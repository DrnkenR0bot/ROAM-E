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

# Initialize left and right motors
left_motor = Motor(board.GP10, board.GP11, down_calibrate=1.0)
right_motor = Motor(board.GP8, board.GP9, down_calibrate=1.0)

# Initialize Loco(motion) control
loco = Loco(left_motor, right_motor)
loco.stop()


#
# Function definitions
#

def distance(cm2xscale: float = 1.):
    """
    Return sonar distance to object.
    
    :param cm2xscale: Use to scale from native cm to any units. Default is meters (1e-2).
    """
    return sonar.distance*cm2xscale

def statistical_distance(
        cm2xscale: float = 1., 
        samples: int = 10, 
        sample_interval: float = 0.01
        ):
    d = []
    for i in range(samples):
        d.append(distance(cm2xscale=cm2xscale))
        time.sleep(sample_interval)
    return sum(d)/samples

def cliff_detect(ground_distance = 10., delta = 5.):
    if cliff_sensor.distance >= (ground_distance + delta):
        return True
    else:
        return False

def beep(buzzer, frequency, duration: float = 0.5, volume_exponent: int = 11):
    if volume_exponent > 15:
        ON = 2**15
    else:
        ON = 2**volume_exponent
    OFF = 0
    buzzer.frequency = int(frequency)
    buzzer.duty_cycle = ON
    time.sleep(duration)
    buzzer.duty_cycle = OFF


#
# Main
#
if __name__ == "__main__":

    # Power up buzzer tones
    for key, _ in cMaj_scale.items():
        if key[0] == "G":
            beep(piezo, cMaj_scale[key], duration=0.1)

    # Servo test
    sa.angle = 0
    sb.angle = 0
    time.sleep(0.5)
    for angle in range(0, 180, 5):
        sa.angle = angle
        sb.angle = angle
        time.sleep(0.2)
    sa.angle = 90
    sb.angle = 90

    # Motor test
    loco.forward(speed=0.5)
    time.sleep(3)
    loco.stop()
    right_motor.forward()
    time.sleep(1)
    loco.stop()
    left_motor.forward()
    time.sleep(1)
    loco.stop()

    while True:
        print(statistical_distance())
        if cliff_detect():
            print("CLIF DETECTED!")
        time.sleep(1)
