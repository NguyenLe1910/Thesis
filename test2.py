import time
# Import mavutil
from pymavlink import mavutil

def wait_conn(self):
    """
    Sends a ping to stabilish the UDP communication and awaits for a response
    """
    msg = None
    while not msg:
        self.mav.ping_send(
            int(time.time() * 1e6), # Unix time in microseconds
            0, # Ping number
            0, # Request ping of all systems
            0 # Request ping of all components
        )
        msg = self.recv_match()
        print('Try to connecting....')
        time.sleep(0.5) 
    print('Connected')

def force_arm(self):
    self.mav.command_long_send(master.target_system,master.target_component,mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,0,1, 21196 , 0, 0, 0, 0, 0)

    try:
        # wait until arming confirmed (can manually check with master.motors_armed())
        print("Force the vehicle to arm")
        self.motors_armed_wait()
        timestamp =self.time_since(motors_armed_wait)
        print('Armed!')
    except:
        print('Cannot Force Arm')

def disarm(self):
    self.mav.command_long_send(master.target_system,master.target_component,mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,0, 0, 0, 0, 0, 0, 0, 0)

    try:
        # wait until arming confirmed (can manually check with master.motors_armed())
        print("Disarm the vehicle")
        self.motors_armed_wait()
        timestamp =self.time_since(motors_armed_wait)
        print('Disarm!')
    except:
        print('Cannot Disarm')

def connect(self):
    print("Heartbeat from system (system %u component %u)" % (self.target_system, self.target_component))
    msg_attitude =  self.recv_match(type='ATTITUDE',blocking=True)

def connecting(self):
    self = mavutil.mavlink_connection('/dev/serial0',baud=916200)

def main():
    connecting()
    wait_conn()

main()
