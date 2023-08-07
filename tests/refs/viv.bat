call abaqus j=in_place ask_delete=no cpus=2 -int
call abaqus python in_place_pp.py
call abaqus j=modal ask_delete=no cpus=2 -int
call abaqus python modal_pp.py