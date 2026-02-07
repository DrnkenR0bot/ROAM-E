import time
import board
import pwmio
import digitalio
from adafruit_motor import servo
import adafruit_hcsr04
from motor_dr import Motor, Loco


# Initialize sonar
sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.GP1, echo_pin=board.GP0)

pa = pwmio.PWMOut(board.GP12, duty_cycle=2**15, frequency=100)
pb = pwmio.PWMOut(board.GP13, duty_cycle=2**15, frequency=100)

sa = servo.Servo(pa)
sb = servo.Servo(pb)





def distance(cm2xscale: float = 1.e-2):
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





while True:
    print(statistical_distance(cm2xscale=1.))
    time.sleep(1)
