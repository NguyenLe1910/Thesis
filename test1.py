import time
import json
# Import mavutil
from pymavlink import mavutil

count_recieve_msg =0
arm = 0
master = mavutil.mavlink_connection('/dev/serial0',baud=916200)

def wait_conn():
    """
    Sends a ping to stabilish the UDP communication and awaits for a response
    """
    msg = None
    while not msg:
        wait_conn = 0
        master.mav.ping_send(
            int(time.time() * 1e6), # Unix time in microseconds
            0, # Ping number
            0, # Request ping of all systems
            0 # Request ping of all components
        )
        msg = master.recv_match()
        print('Try to connecting....')
        time.sleep(0.5)
    wait_conn = 1; 
    print('Connected')

def force_arm():
    try:
        master.mav.command_long_send(master.target_system,master.target_component,
                                    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,0,1, 21196 , 0, 0, 0, 0, 0)
        ack_msg = master.recv_match(type='COMMAND_ACK',blocking=True)
        print(ack_msg)
    except :
        print('Can not arm')

def disarm():
    master.mav.command_long_send(master.target_system,master.target_component,mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,0, 0, 0, 0, 0, 0, 0, 0)
    
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

def set_rc_channel_pwm(channel_id, pwm=1500):
    """ Set RC channel pwm value
    Args:
        channel_id (TYPE): Channel ID
        pwm (int, optional): Channel pwm value 1100-1900
    """
    if channel_id < 1 or channel_id > 10:
        print("Channel does not exist.")
        return

    rc_channel_values = [65535 for _ in range(18)]
    rc_channel_values[channel_id - 1] = pwm
    master.mav.rc_channels_override_send(
        master.target_system,                # target_system
        master.target_component,             # target_component
        *rc_channel_values)                  # RC channel list, in microseconds.

def msg_attitude():
    global count_recieve_msg
    count_recieve_msg = count_recieve_msg +1
    return master.recv_match(type='ATTITUDE',blocking=True)

def msg_GPS_RAW():
    return master.recv_match(type='GPS_RAW_INT',blocking=True)


def arm_test():
    print('Try to Arm')
    time.sleep(3)
    print('Can not Arm !')

def force_arm_test():
    print('Try to Arm')
    time.sleep(0.7)
    print('Arming!')

def disarm_test():
    print('Try to Disarm')
    time.sleep(0.7)
    print('Disarm !')

wait_conn()