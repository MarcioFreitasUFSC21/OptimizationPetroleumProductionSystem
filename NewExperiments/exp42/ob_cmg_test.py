import math
from math import *

from ob_util import *
from ob_cmg import *


logger = get_logger(__name__)

def ob_compute(sim_data):
    """ Function to perform outboard computations and analyses.
    Args:
        sim_data (class Sim_Data):  Variable storing the simulation data.
    Returns:
        ob_data (class OB_Data):
            ob_data.set_status(status): Method to set outboard (script) status.
                             Accepted values for "status":
                                - OB_Status.READY: Outboard software is ready (1)
                                - OB_Status.TERMINATE_NEXT_COM_TIME: Outboard software terminates at next communication time (9)
                                - OB_Status.NORMAL_TERMINATE: Outboard software terminated normally (-100)
                                - OB_Status.ABNORMAL_TERMINATE: Outboard software terminated abnormally (-101)
            ob_data.info_to_sim(data): Method to set outboard data to be written into outboard data file (root.obfname.data).
                            Conditions for "data":
                                - Must be a string
                                - Must follow the host(simulator) keyword system
                                - Each call to info_to_sim writes provided data on a line
            ob_data.message(msg): Method to set message(s) to be logged or shown on screen.
            ob_data.set_WCURRCN(wells, wcurrcn_flag): Method to set the *WCURRCN keyword for a well or a list of wells.
                            Conditions for "wells":
                                - Can be a single well name, e.g. ob_data.set_WCURRCN('PRODUCER1', 'ON')
                                - Can be a list of well names, e.g. ob_data.set_WCURRCN(['PRODUCER1', 'PRODUCER2'], 'OFF')
                            Conditions for "wcurrcn_flag":
                                - Can be either "ON" or "OFF" as explained in host users' manual
    """

    ob_data = OB_Data()

    ####### START OUTBOARD COMPUTATIONS HERE #######
    if sim_data.TIMECURR == 0.0:
        # This condition prevents outboard update before the first timestep.
        return ob_data

    # Extract required data from sim_data().
    cur_Tim = sim_data.TIMECURR
    cur_BHP = sim_data.WELLS['PRODUCER1'].BHP
    cur_STO = sim_data.WELLS['PRODUCER1'].STO
    cur_STG = sim_data.WELLS['PRODUCER1'].STG
#********************************************************************************
#                       The Auxiliary variables
#********************************************************************************
    limRGO = 100
    limSTO = 75
    limk   = 1.50

    if cur_STO > 0.0:
        cur_GOR = cur_STG / cur_STO
    else:
        cur_GOR = 0.0

    if cur_GOR > limRGO:
        new_BHP = min( cur_BHP * limk, 2500 )
        ob_data.info_to_sim("ALTER 'PRODUCER1'")
        ob_data.info_to_sim(f"\t{new_BHP}")
        ob_data.message(f"   OB Event ({cur_Tim:^10.2f} days ):\tChoking back well to control GOR.")

    if cur_STO < limSTO:
        ob_data.info_to_sim("SHUTIN 'PRODUCER1'")
        ob_data.message(f"   OB Event ({cur_Tim:^10.2f} days ):\tShuting in Well due to low oil rate.")

    ####### END OUTBOARD COMPUTATIONS HERE #######

    return ob_data

if __name__ == '__main__':
    ob_imex = OB_CMG(ob_compute)
    ob_imex.run()
