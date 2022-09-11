import time
# Import mavutil
from pymavlink import mavutil

def wait_conn():
    """
    Sends a ping to stabilish the UDP communication and awaits for a response
    """
    msg = None
    while not msg:
        master.mav.ping_send(
            int(time.time() * 1e6), # Unix time in microseconds
            0, # Ping number
            0, # Request ping of all systems
            0 # Request ping of all components
        )
        msg = master.recv_match()
        print('Try to connecting....')
        time.sleep(0.5)
    print('Connected')    

def force_arm(self):
    master.mav.command_long_send(master.target_system,master.target_component,mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,0,1, 0, 0, 0, 0, 0, 0)

    try:
        # wait until arming confirmed (can manually check with master.motors_armed())
        print("Force the vehicle to arm")
        master.motors_armed_wait()
        timestamp =master.time_since(motors_armed_wait)
        print('Armed!')
    except:
        print('Cannot Force Arm')

def setmode(mode):
    # Check if mode is available
    if mode not in master.mode_mapping():
        print('Unknown mode : {}'.format(mode))
        print('Try:', list(master.mode_mapping().keys()))

    # Get mode ID
    mode_id = master.mode_mapping()[mode]
    master.mav.set_mode_send(master.target_system,mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,mode_id)
    ack_msg = master.recv_match(type='COMMAND_ACK',blocking=True)
    print(ack_msg)

def connect():
    master = mavutil.mavlink_connection('/dev/serial0',baud=916200)
    wait_conn()
    print("Heartbeat from system (system %u component %u)" % (master.target_system, master.target_component))
