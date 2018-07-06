# used for pixel tracking
# by Whyjay Zheng, Jul 6 2018
# requires isce >= 2.0.0

import isce
from mroipac.ampcor.Ampcor import Ampcor
# from isceobj.Image.Image import Image
import multiprocessing as mp
from functools import partial
import numpy as np

def create_ampcor_task(ini):
	a = Ampcor()
	a.imageDataType1 = 'real'
	a.imageDataType2 = 'real'
	a.margin = 1
	a.acrossGrossOffset = 0
	a.downGrossOffset = 0
	a.skipSampleAcross = None
	a.skipSampleDown = None
	a.windowSizeHeight = ini.pxsettings['refwindow_y']
	a.windowSizeWidth = ini.pxsettings['refwindow_x']
	a.searchWindowSizeHeight = ini.pxsettings['searchwindow_y']
	a.searchWindowSizeWidth = ini.pxsettings['searchwindow_x']
	a.numberLocationAcross = ini.pxsettings['size_across']
	a.numberLocationDown = ini.pxsettings['size_down']      # waiting to be modified
	a.firstSampleAcross = 1
	a.oversamplingFactor = ini.pxsettings['oversampling']
	return a

def multicore_ampcor(downrange, a, imgpair):
	a.firstSampleDown = downrange[0]
	a.lastSampleDown = downrange[1]
	# a.ampcor(obj, obj2, 0, 0)   # band 0, band 0
	a.ampcor(imgpair[0].iscepointer, imgpair[1].iscepointer)
	return a

def ampcor_task(imgpair, ini):
	a = create_ampcor_task(ini)
	downrange = []
	downsize = imgpair[0].GetRasterYSize()
	threads = ini.pxsettings['threads']
	downsize_each = int(downsize / threads)
	for i in range(threads):
		downrange.append([i * downsize_each + 1, i * downsize_each + downsize_each])
	downrange[-1] = [i * downsize_each + 1, downsize]
	pool = mp.Pool()
	poolwork = partial(multicore_ampcor, a=a, imgpair=imgpair)
	task_result = pool.map(poolwork, downrange)
	return task_result

def writeout_ampcor_task(task_result, ini):
	field_list = [np.array(i.getOffsetField().unpackOffsets()) for i in task_result]
	field = np.vstack(field_list)
	cov1 = np.hstack([np.array(i.getCov1()) for i in task_result])
	cov2 = np.hstack([np.array(i.getCov2()) for i in task_result])
	cov3 = np.hstack([np.array(i.getCov3()) for i in task_result])
	cov = np.stack([cov1, cov2, cov3])
	complete_set = np.concatenate([field, cov.T], axis = 1)
	np.savetxt(ini.result['ampcor_results'], complete_set, delimiter=" ", fmt='%5d %10.6f %5d %10.6f %10.6f %11.6f %11.6f %11.6f')