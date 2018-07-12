# used for pixel tracking
# by Whyjay Zheng, Jul 6 2018
# requires isce >= 2.0.0

import isce
from mroipac.ampcor.Ampcor import Ampcor
# from isceobj.Image.Image import Image
import multiprocessing as mp
from functools import partial
import numpy as np

class Ampcor_Corrected(Ampcor):

    def checkSkip(self):
        '''
        The corrected version of checkSkip. 
        Corrected the issue that program crashes when using skip number instead of size number.
        '''

        xMargin = 2*self.searchWindowSizeWidth + self.windowSizeWidth
        yMargin = 2*self.searchWindowSizeHeight + self.windowSizeHeight
        if self.scaleFactorY is None:
            if (self.prf1 is None) or (self.prf2 is None):
                self.scaleFactorY = 1.
            else:
                self.scaleFactorY = self.prf2 / self.prf1

        if (self.scaleFactorY < 0.9) or (self.scaleFactorY > 1.1):
            raise ValueError('Ampcor is designed to work on images with maximum of 10%% scale difference in azimuth. Attempting to use images with scale difference of %2.2f'%(self.scaleFactorY))

        if self.scaleFactorX is None:
            if (self.rangeSpacing1 is None) or (self.rangeSpacing2 is None):
                self.scaleFactorX = 1.
            else:
                self.scaleFactorX = self.rangeSpacing1/self.rangeSpacing2

        if (self.scaleFactorX < 0.9) or (self.scaleFactorX > 1.1):
            raise ValueError('Ampcor is designed to work on images with maximum of 10%% scale difference in range. Attempting to use images with scale difference of %2.2f'%(self.scaleFactorX))

        print('Scale Factor in Range: ', self.scaleFactorX)
        print('Scale Factor in Azimuth: ', self.scaleFactorY)

        offAcmax = int(self.acrossGrossOffset + (self.scaleFactorX-1)*self.lineLength1)

        offDnmax = int(self.downGrossOffset + (self.scaleFactorY-1)*self.fileLength1)

        if self.firstSampleDown is None:
            self.firstSampleDown = max(self.margin, -self.downGrossOffset) + yMargin + 1

        if self.lastSampleDown is None:
            self.lastSampleDown = int( min(self.fileLength1, self.fileLength2-offDnmax) - yMargin - 1 - self.margin)

        if (self.skipSampleDown is None) and (self.numberLocationDown is not None):
            self.skipSampleDown = int((self.lastSampleDown - self.firstSampleDown) / (self.numberLocationDown - 1.))
            print('Skip Sample Down: %d'%(self.skipSampleDown))
        elif self.skipSampleDown is not None:
        	print('Skip Sample Down: %d'%(self.skipSampleDown))
        else:
            raise ValueError('Both skipSampleDown and numberLocationDown undefined. Need atleast one input.')

        if self.firstSampleAcross is None:
            self.firstSampleAcross = max(self.margin, -self.acrossGrossOffset) + xMargin + 1

        if self.lastSampleAcross is None:
            self.lastSampleAcross = int(min(self.lineLength1, self.lineLength2 - offAcmax) - xMargin - 1 -self.margin)

        if (self.skipSampleAcross is None) and (self.numberLocationAcross is not None):
            self.skipSampleAcross = int((self.lastSampleAcross - self.firstSampleAcross) / (self.numberLocationAcross - 1.))
            print('Skip Sample Across: %d'%(self.skipSampleAcross))
        elif self.skipSampleAcross is not None:
        	print('Skip Sample Across: %d'%(self.skipSampleAcross))
        else:
            raise ValueError('Both skipSampleDown and numberLocationDown undefined. Need atleast one input.')


def create_ampcor_task(ini):
	a = Ampcor_Corrected()
	a.imageDataType1 = 'real'
	a.imageDataType2 = 'real'
	a.margin = 0
	a.acrossGrossOffset = 0
	a.downGrossOffset = 0
	# a.skipSampleAcross = None
	# a.skipSampleDown = None
	a.windowSizeHeight = ini.pxsettings['refwindow_y']
	a.windowSizeWidth = ini.pxsettings['refwindow_x']
	a.searchWindowSizeHeight = ini.pxsettings['searchwindow_y']
	a.searchWindowSizeWidth = ini.pxsettings['searchwindow_x']
	a.numberLocationAcross = ini.pxsettings['size_across']
	a.numberLocationDown = ini.pxsettings['size_down']      # waiting to be modified
	a.skipSampleAcross = ini.pxsettings['skip_across']
	a.skipSampleDown = ini.pxsettings['skip_down']          # waiting to be modified
	a.oversamplingFactor = ini.pxsettings['oversampling']
	return a

def multicore_ampcor(downrange, a, imgpair):
	a.firstSampleAcross = 1
	a.lastSampleAcross = imgpair[0].GetRasterXSize()
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

# ===== params that have not been addressed yet
# complex number
#	a.margin = 1
#	a.acrossGrossOffset = 0
#	a.downGrossOffset = 0
#	a.firstSampleAcross = 1
#	a.firstSampleDown = downrange[0]
#	a.lastSampleDown = downrange[1]