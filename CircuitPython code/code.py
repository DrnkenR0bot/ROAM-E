import time
import board
import pwmio
#import simpleio
#import digitalio
import adafruit_hcsr04
from adafruit_motor import servo
from note_frequencies import cMaj_scale
#from motor_dr import Motor, Loco


# Initialize piezo buzzer
piezo = pwmio.PWMOut(board.GP22, variable_frequency=True)

# Initialize sonar
sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.GP1, echo_pin=board.GP0)

# Initialize servos
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




if __name__ == "__main__":

    for key, value in cMaj_scale.items():
        if key[0] == "G":
            beep(piezo, cMaj_scale[key], duration=0.1)

    while True:
        print(statistical_distance(cm2xscale=1.))
        time.sleep(1)
