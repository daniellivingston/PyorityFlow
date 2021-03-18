import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

from rpy2 import robjects
import rpy2.robjects as R
from rpy2.robjects.vectors import IntVector, FloatVector
from rpy2.robjects.packages import importr, data
from rpy2.rinterface_lib.embedded import RRuntimeError
import warnings

import rpy2.rinterface as ri

from rpy2.robjects import numpy2ri
numpy2ri.activate()

ri.initr()
RNone = ri.MissingArg

pf = importr('PriorityFlow')

RGetMat = lambda key: np.asarray(R.r[key])
RListGet = lambda RList, key: np.asarray(RList.rx2(key))

class TestData:
    DEM = RGetMat('DEM')
    watershed_mask = RGetMat('watershed.mask')
    river_mask = RGetMat('river.mask')

class PFQueue():
    def __init__(self, init):
        self._view = init
        self.mask = RListGet(init, 'mask')
        self.queue = RListGet(init, 'queue')
        self.marked = RListGet(init, 'marked')
        self.basins = RListGet(init, 'basins')
        self.direction = RListGet(init, 'direction')

def _pfprocess(view, keys):
    results = {}

    for key in keys:
        results[key] = RListGet(view, key)
    
    return results


def InitQueue(dem, initmask = None, domainmask = None, d4:tuple = (1,2,3,4)):
    # https://github.com/lecondon/PriorityFlow/blob/master/Rpkg/R/Init_Queue.R#L18

    if initmask is None:
        initmask = RNone
    if domainmask is None:
        domainmask = RNone
    
    d4 = IntVector(d4)

    results = pf.InitQueue(dem=dem,initmask=initmask,domainmask=domainmask,d4=d4)
    
    #return PFQueue(results)
    return _pfprocess(results, ["mask", "queue", "marked", "basins", "direction"])

# https://github.com/lecondon/PriorityFlow/blob/master/Rpkg/R/D4_Traverse.R#L22
def D4TraverseB(dem, queue, marked, mask=None, step=None, direction=None, basins=None, d4: tuple = (1,2,3,4), printstep = False, nchunk = 100, epsilon = 0, printflag = False):
    
    if mask is None:
        mask = RNone
    if step is None:
        step = RNone
    if direction is None:
        direction = RNone
    if basins is None:
        basins = RNone
    
    d4 = IntVector(d4)

    results = pf.D4TraverseB(dem=dem, queue=queue, marked=marked, mask=mask, step=step, direction=direction, basins=basins, d4 = d4, printstep = printstep, nchunk = nchunk, epsilon=epsilon, printflag=printflag)
    return _pfprocess(results, ["dem", "mask", "marked", "step", "direction", "basins"])

    # returns list("dem"=demnew, "mask"=mask, "marked"=marked, "step"= step, "direction"=direction, "basins"=basins)



# drainageArea=function(direction, mask, d4=c(1,2,3,4), printflag=F)
# https://github.com/lecondon/PriorityFlow/blob/master/Rpkg/R/drainage_area.R
def drainageArea(direction, mask = None, d4: tuple = (1, 2, 3, 4), printflag = False):
    if mask is None:
        mask = RNone
    
    d4 = IntVector(d4)

    results = pf.drainageArea(direction = direction, mask = mask, d4 = d4, printflag = printflag)
    return _pfprocess(results, ["drainarea"])



# CalcSubbasins=function(direction, area, mask, d4=c(1,2,3,4), riv_th=50, printflag=F, merge_th=0)
# https://github.com/lecondon/PriorityFlow/blob/master/Rpkg/R/Define_Subbasins.R
def CalcSubbasins(direction, area, mask = None, d4=(1,2,3,4), riv_th=50, printflag=False, merge_th=0):
    if mask is None:
        mask = RNone
    
    d4 = IntVector(d4)

    results = pf.CalcSubbasins(direction=direction, area=area, mask=mask, d4=d4, riv_th=riv_th, printflag=printflag, merge_th=merge_th)
    # list("segments"=subbasin, "subbasins"=subbasinA, "RiverMask"=rivers, "summary"=summary)
    return _pfprocess(results, ["segments", "subbasins", "RiverMask", "summary"])



# RiverSmooth=function(dem, direction, mask, river.summary, river.segments, bank.epsilon=0.01, river.epsilon=0.0,  d4=c(1,2,3,4), printflag=F)
# https://github.com/lecondon/PriorityFlow/blob/master/Rpkg/R/River_Smoothing.R#L27
def RiverSmooth(dem, direction, river_summary, river_segments, mask=None, bank_epsilon=0.01, river_epsilon=0.0,  d4:tuple=(1,2,3,4), printflag=False):

    if mask is None:
        mask = RNone
    
    d4 = IntVector(d4)

    results = pf.RiverSmooth(dem=dem, direction=direction, mask=mask, river_summary=river_summary, river_segments=river_segments, bank_epsilon=bank_epsilon, river_epsilon=river_epsilon, d4=d4, printflag=printflag)
    return _pfprocess(results, ["dem.adj", "processed", "summary"])

#PathExtract
#SlopeCalStan

