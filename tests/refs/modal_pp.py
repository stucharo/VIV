import numpy as np

import odbAccess

odb = odbAccess.openOdb("modal.odb")

s = odb.steps["Step-2"]
nodes = odb.rootAssembly.instances["PART-1-1"].nodes

modes = len(s.frames)

freqs = []

for m in range(modes - 1):
    f = s.frames[m + 1]
    freqs.append(f.frequency)
    ms = np.zeros((len(nodes) - 1, 3))
    for n in range(len(nodes) - 1):
        ms[n, :] = f.fieldOutputs["U"].values[n].data
    fname = "mode_{0}.dat".format(m + 1)
    np.savetxt(fname, ms, delimiter=",")

np.savetxt("freqs.dat", freqs, delimiter=",")
