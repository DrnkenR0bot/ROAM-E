"""
DrnkenR0bot DC motor library for 2 motor locomotion.

Motor calibration might be necessary due to manufacturing differences
between motors. Use "down_calibrate" to scale the max speed of an
individual motor through trial and error until straight forward
driving is achieved. 
Note: If robot skews right, down calibrate left motor.

"""
import time
import pwmio

class Motor:
    def __init__(self, pin1, pin2, frequency=2000, down_calibrate=1.0):
        self.IN1 = pwmio.PWMOut(pin1, frequency=frequency)
        self.IN2 = pwmio.PWMOut(pin2, frequency=frequency)
        self.max_duty_cycle = int(65535*down_calibrate)
        self.min_duty_cycle = 0

    def stop(self):
        self.IN1.duty_cycle = 0
        self.IN2.duty_cycle = 0

    def forward(self, speed: float = 1.0):
        self.IN1.duty_cycle = int(self.max_duty_cycle*speed)
        self.IN2.duty_cycle = 0 

    def backward(self, speed: float = 1.0):
        self.IN1.duty_cycle = 0
        self.IN2.duty_cycle = int(self.max_duty_cycle*speed)


class Loco:
    def __init__(self, left_motor: Motor, right_motor: Motor):
        self.left_motor = left_motor
        self.right_motor = right_motor

    def stop(self):
        self.left_motor.stop()
        self.right_motor.stop()

    def forward(self, speed: float = 1.0):
        self.left_motor.forward(speed=speed)
        self.right_motor.forward(speed=speed)

    def backward(self, speed: float = 1.0):
        self.left_motor.backward(speed=speed)
        self.right_motor.backward(speed=speed)

    def right_spin(self, speed: float = 0.25):
        self.left_motor.forward(speed=speed)
        self.right_motor.backward(speed=speed)

    def left_spin(self, speed: float = 0.25):
        self.left_motor.backward(speed=speed)
        self.right_motor.forward(speed=speed)

    def right_turn(self, speed: float = 0.25, turn_time: float = 1):
        self.left_motor.forward(speed=speed)
        self.right_motor.backward(speed=speed)
        time.sleep(turn_time)
        self.stop()

    def left_turn(self, speed: float = 0.25, turn_time: float = 1):
        self.left_motor.backward(speed=speed)
        self.right_motor.forward(speed=speed)
        time.sleep(turn_time)
        self.stop()

    def ramp_forward(self, max_speed: float = 1.0, time_duration: float = 0.5, steps: int = 20):
        self.stop()
        interval = time_duration/steps
        new_speed = 0.
        for i in range(steps):
            new_speed = new_speed + max_speed/steps
            self.forward(speed=new_speed)
            time.sleep(interval)

