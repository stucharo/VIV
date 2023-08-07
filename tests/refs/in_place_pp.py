import numpy as np

import odbAccess

odb = odbAccess.openOdb("in_place.odb")
u = odb.steps["Step-2"].frames[-1].fieldOutputs["U"]
n = odb.rootAssembly.instances["PART-1-1"].nodes
seabed_segments = odb.rootAssembly.instances["SEABED"].analyticSurface.segments

seabed_surface = np.zeros((len(seabed_segments), 2))
for i in range(len(seabed_segments)):
    coords = seabed_segments[i].data[0]
    seabed_surface[i, 0] = coords[0]
    seabed_surface[i, 1] = coords[1]

with open("in_place_nodes.dat", "w") as f:
    f.write("*NODE, NSET=PIPE\n")

    with open("gaps.dat", "w") as c:
        for i in range(len(n) - 1):
            # get displaced coordinates
            x = n[i].coordinates[0] + u.values[i].data[0]
            y = n[i].coordinates[1] + u.values[i].data[1]

            node = i + 1
            # interpolate seabed elevation below node and calculate vertical gap
            # this is required because COPEN also considers the wall of the span
            sb_elevation = np.interp(x, seabed_surface[:, 0], seabed_surface[:, 1])
            gap = y - sb_elevation
            # write modal node file
            f.write("{0:4d}, {1:9.3e}, {2:9.3e}, 0\n".format(node, x, y))
            # write gap file
            c.write("{0:4d}, {1:9.3e}\n".format(node, y - sb_elevation))
