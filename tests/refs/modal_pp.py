import numpy as np

import odbAccess

odb = odbAccess.openOdb("modal.odb")

s = odb.steps["Step-2"]
nodes = odb.rootAssembly.instances["PART-1-1"].nodes

modes = len(s.frames)

freqs = []

for m in range(1, modes):
    f = s.frames[m]
    freqs.append(f.frequency)
    ms = np.zeros((len(nodes), 3))
    for n in range(len(nodes)):
        ms[n, :] = f.fieldOutputs["U"].values[n].data
    fname = "mode_{0}.dat".format(m)
    np.savetxt(fname, ms, delimiter=",")

np.savetxt("freqs.dat", freqs, delimiter=",")
