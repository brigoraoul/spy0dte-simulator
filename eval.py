from eval_functions import run_total_eval
from strategies.strategies import *

def mm_tuning(quicktest=False, experiment_name="MM Tuning"):
    print("Start MM Tuning. Quicktest: ", quicktest)
    if quicktest:
        experiment_name = "Quicktest/MM Tuning"
    # run tuning
    param_settings = [
        # Format: (stop loss, take profit)
        (1, 2),
        (1, 2.5),
        (1, 3),
        (1, 3.5),
        (1, 4),
        (1.5, 1.5),
        (1.5, 2.5),
        (1.5, 2),
        (2, 1.5),
        (2, 2),
        (2, 3),
        (2, 4)
    ]
    for setting in param_settings:
        run_total_eval(experiment_name=experiment_name, 
                       run_name=f"SL: {setting[0]}, TP: {setting[1]}", 
                       stop_loss=setting[0], 
                       take_profit=setting[1], 
                       quicktest=quicktest)
        

def time_window_tuning(quicktest=False):
    print("Start Time Window Tuning. Quicktest: ", quicktest)
    experiment_name = "ZeroTheta Time Window Tuning"
    if quicktest:
        experiment_name = "Quicktest/Time Window"

    param_settings = [
        # Format: (start time, end time)
       # ("13:00", "15:00"),
       # ("15:00", "17:00"),
       # ("17:00", "19:00"),
        ("13:30", "21:00"),
        ("15:30", "21:00"),
        ("17:00", "21:00"),
        ("19:00", "21:00"),
        ("20:00", "21:45"),
    ]
    for setting in param_settings:
        run_total_eval(experiment_name=experiment_name, 
                       run_name=f"Start: {setting[0]}, End: {setting[1]}", 
                       start_time=setting[0], 
                       end_time=setting[1], 
                       quicktest=quicktest)


#time_window_tuning(quicktest=True)
#mm_tuning(experiment_name="Exit SL/TP stops")

# regular run quicktest
#run_total_eval("Quicktest/Eval", run_name="LHL Formation", strategy=LHLFormation(), quicktest=True)

#run_total_eval(experiment_name="ZeroTheta Eval", run_name="Exit Midpoint", exit_w_open=False)
#run_total_eval(experiment_name="ZeroTheta Eval", run_name="Exit Open", exit_w_open=True)

#run_total_eval(experiment_name="Exit SL/TP stops", exit_w_mm=True)

run_total_eval(experiment_name="ZeroTheta Spread Calculation Strat", run_name="Enforce OTM", enforce_ITM=False, middle_ITM=False, enforce_OTM=True)
run_total_eval(experiment_name="ZeroTheta Spread Calculation Strat", run_name="Enforce ITM", enforce_ITM=True, middle_ITM=False, enforce_OTM=False)
run_total_eval(experiment_name="ZeroTheta Spread Calculation Strat", run_name="Middle ITM", enforce_ITM=False, middle_ITM=True, enforce_OTM=False)
run_total_eval(experiment_name="ZeroTheta Spread Calculation Strat", run_name="ITM / OTM", enforce_ITM=False, middle_ITM=False, enforce_OTM=False)