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

def force_arm():
    print("Force the vehicle to arm")

    master.mav.command_long_send(master.target_system,master.target_component,mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,0,1, 21196, 0, 0, 0, 0, 0)

    #msg = master.recv_match(type="COMMAND_ACK",blocking=True)
    #print(msg)

    # wait until arming confirmed (can manually check with master.motors_armed())
    print("Waiting for the vehicle to force arm")
    master.motors_armed_wait()
    print('Armed!')


master = mavutil.mavlink_connection('/dev/serial0',baud=916200)

wait_conn()
force_arm()