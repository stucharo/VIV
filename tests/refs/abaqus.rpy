# -*- coding: mbcs -*-
#
# Abaqus/Viewer Release 6.14-4 replay file
# Internal Version: 2015_06_11-21.41.13 135079
# Run by roys on Tue Aug 08 13:08:40 2023
#

# from driverUtils import executeOnCaeGraphicsStartup
# executeOnCaeGraphicsStartup()
#: Executing "onCaeGraphicsStartup()" in the site directory ...
from abaqus import *
from abaqusConstants import *
session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=192.958847045898, 
    height=153.481475830078)
session.viewports['Viewport: 1'].makeCurrent()
session.viewports['Viewport: 1'].maximize()
from viewerModules import *
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
o2 = session.openOdb(name='modal.odb')
#: Model: C:/Users/roys/OneDrive - TECHNIPFMC/Dev/Abaqus/viv/tests/refs/modal.odb
#: Number of Assemblies:         1
#: Number of Assembly instances: 0
#: Number of Part instances:     1
#: Number of Meshes:             1
#: Number of Element Sets:       6
#: Number of Node Sets:          2
#: Number of Steps:              2
session.viewports['Viewport: 1'].setValues(displayedObject=o2)
session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
    variableLabel='U', outputPosition=NODAL, refinement=(INVARIANT, 
    'Magnitude'), )
session.viewports['Viewport: 1'].odbDisplay.display.setValues(
    plotState=CONTOURS_ON_DEF)
session.viewports['Viewport: 1'].odbDisplay.setFrame(step=1, frame=2 )
session.viewports['Viewport: 1'].odbDisplay.setFrame(step=1, frame=3 )
session.viewports['Viewport: 1'].odbDisplay.setFrame(step=1, frame=4 )
session.viewports['Viewport: 1'].odbDisplay.setFrame(step=1, frame=5 )
session.viewports['Viewport: 1'].odbDisplay.setFrame(step=1, frame=6 )
session.viewports['Viewport: 1'].odbDisplay.setFrame(step=1, frame=7 )
session.viewports['Viewport: 1'].odbDisplay.setFrame(step=1, frame=8 )
session.viewports['Viewport: 1'].odbDisplay.setFrame(step=1, frame=7 )
session.viewports['Viewport: 1'].odbDisplay.setFrame(step=1, frame=6 )
session.viewports['Viewport: 1'].odbDisplay.setFrame(step=1, frame=5 )
session.viewports['Viewport: 1'].odbDisplay.setFrame(step=1, frame=4 )
session.viewports['Viewport: 1'].odbDisplay.setFrame(step=1, frame=3 )
session.viewports['Viewport: 1'].odbDisplay.setFrame(step=1, frame=2 )
session.viewports['Viewport: 1'].odbDisplay.setFrame(step=1, frame=1 )
session.viewports['Viewport: 1'].odbDisplay.setFrame(step=1, frame=2 )
session.viewports['Viewport: 1'].odbDisplay.setFrame(step=1, frame=3 )
session.viewports['Viewport: 1'].odbDisplay.setFrame(step=1, frame=4 )
session.viewports['Viewport: 1'].odbDisplay.setFrame(step=1, frame=5 )
session.viewports['Viewport: 1'].odbDisplay.setFrame(step=1, frame=6 )
session.viewports['Viewport: 1'].odbDisplay.setFrame(step=1, frame=5 )
session.viewports['Viewport: 1'].odbDisplay.setFrame(step=1, frame=4 )
session.viewports['Viewport: 1'].odbDisplay.setFrame(step=1, frame=3 )
session.viewports['Viewport: 1'].odbDisplay.setFrame(step=1, frame=2 )
session.viewports['Viewport: 1'].odbDisplay.setFrame(step=1, frame=1 )
session.viewports['Viewport: 1'].view.setValues(nearPlane=1048.83, 
    farPlane=1326.45, width=122.515, height=47.1806, viewOffsetX=12.3843, 
    viewOffsetY=18.266)
session.viewports['Viewport: 1'].view.setValues(session.views['Top'])
session.viewports['Viewport: 1'].view.setValues(nearPlane=736.684, 
    farPlane=871.748, width=822.076, height=316.582, viewOffsetX=21.4719, 
    viewOffsetY=43.0345)
session.viewports['Viewport: 1'].view.setValues(nearPlane=789.687, 
    farPlane=818.745, width=176.529, height=67.9815, viewOffsetX=0.780255, 
    viewOffsetY=6.38345)
#: 
#: Node: PART-1-1.115
#:                                         1             2             3        Magnitude
#: Base coordinates:                  1.14000e+002, -5.79400e-003,  0.00000e+000,      -      
#: Scale:                             4.00000e+001,  4.00000e+001,  4.00000e+001,      -      
#: Deformed coordinates (unscaled):   1.14000e+002, -5.79400e-003, -3.64114e-011,      -      
#: Deformed coordinates (scaled):     1.14000e+002, -5.79400e-003, -1.45645e-009,      -      
#: Displacement (unscaled):           9.00150e-018,  9.66358e-017, -3.64114e-011,  3.64114e-011
#: 
#: Node: PART-1-1.291
#:                                         1             2             3        Magnitude
#: Base coordinates:                  2.90000e+002, -5.79300e-003, -0.00000e+000,      -      
#: Scale:                             4.00000e+001,  4.00000e+001,  4.00000e+001,      -      
#: Deformed coordinates (unscaled):   2.90000e+002, -5.79300e-003, -1.01722e-011,      -      
#: Deformed coordinates (scaled):     2.90000e+002, -5.79300e-003, -4.06889e-010,      -      
#: Displacement (unscaled):           4.19080e-017, -1.13236e-017, -1.01722e-011,  1.01722e-011
#: 
#: Nodes for distance: PART-1-1.115, PART-1-1.291
#:                                        1             2             3        Magnitude
#: Base distance:                     1.76000e+002,  9.99775e-007, -0.00000e+000,  1.76000e+002
#: Scale:                             4.00000e+001,  4.00000e+001,  4.00000e+001,      -      
#: Deformed distance (unscaled):      1.76000e+002,  9.99775e-007,  2.62391e-011,  1.76000e+002
#: Deformed distance (scaled):        1.76000e+002,  9.99775e-007,  1.04957e-009,  1.76000e+002
#: Relative displacement (unscaled):  3.29065e-017, -1.07959e-016,  2.62391e-011,  2.62391e-011
#: 
#: Node: PART-1-1.152
#:                                         1             2             3        Magnitude
#: Base coordinates:                  1.51000e+002, -6.76600e-003,  0.00000e+000,      -      
#: Scale:                             4.00000e+001,  4.00000e+001,  4.00000e+001,      -      
#: Deformed coordinates (unscaled):   1.51000e+002, -6.76600e-003,  6.19154e-005,      -      
#: Deformed coordinates (scaled):     1.51000e+002, -6.76600e-003,  2.47662e-003,      -      
#: Displacement (unscaled):          -3.76729e-017,  5.25494e-017,  6.19154e-005,  6.19154e-005
#: 
#: Node: PART-1-1.250
#:                                         1             2             3        Magnitude
#: Base coordinates:                  2.49000e+002, -6.76600e-003, -0.00000e+000,      -      
#: Scale:                             4.00000e+001,  4.00000e+001,  4.00000e+001,      -      
#: Deformed coordinates (unscaled):   2.49000e+002, -6.76600e-003,  6.23569e-005,      -      
#: Deformed coordinates (scaled):     2.49000e+002, -6.76600e-003,  2.49428e-003,      -      
#: Displacement (unscaled):           4.59921e-017, -1.93710e-017,  6.23569e-005,  6.23569e-005
#: 
#: Nodes for distance: PART-1-1.152, PART-1-1.250
#:                                        1             2             3        Magnitude
#: Base distance:                     9.80000e+001,  0.00000e+000, -0.00000e+000,  9.80000e+001
#: Scale:                             4.00000e+001,  4.00000e+001,  4.00000e+001,      -      
#: Deformed distance (unscaled):      9.80000e+001,  0.00000e+000,  4.41549e-007,  9.80000e+001
#: Deformed distance (scaled):        9.80000e+001,  0.00000e+000,  1.76621e-005,  9.80000e+001
#: Relative displacement (unscaled):  8.36650e-017, -7.19204e-017,  4.41549e-007,  4.41549e-007
