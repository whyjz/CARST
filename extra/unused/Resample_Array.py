# Old code to resample array.
# A newer version is in libdhdt.py.

def Resample_Array(orig_dem, resamp_ref_dem, resamp_method='linear'):

	"""
	resample orig_dem using the extent and spacing provided by resamp_ref_dem
	orig_dem: class UtilRaster.SingleRaster object
	resamp_ref_dem: class UtilRaster.SingleRaster object
	returns: an numpy array, which you can use the methods in UtilRaster to trasform it into a raster

	Uses linear interpolation because it best represent flat ice surface.
	-9999.0 (default nan in a Geotiff) is used to fill area outside the extent of orig_dem.

	resamp_method: 'linear', 'cubic', 'quintic', 'nearest'

	"""
	o_ulx, o_uly, o_lrx, o_lry = orig_dem.get_extent()
	o_ulx, o_xres, o_xskew, o_uly, o_yskew, o_yres = orig_dem.GetGeoTransform()
	orig_dem_extent = Polygon([(o_ulx, o_uly), (o_lrx, o_uly), (o_lrx, o_lry), (o_ulx, o_lry)])
	ulx, uly, lrx, lry = resamp_ref_dem.get_extent()
	ulx, xres, xskew, uly, yskew, yres = resamp_ref_dem.GetGeoTransform()
	resamp_ref_dem_extent = Polygon([(ulx, uly), (lrx, uly), (lrx, lry), (ulx, lry)])
	if orig_dem_extent.intersects(resamp_ref_dem_extent):
		x = np.linspace(o_ulx, o_lrx - o_xres, orig_dem.get_x_size())
		y = np.linspace(o_uly, o_lry - o_yres, orig_dem.get_y_size())
		z = orig_dem.ReadAsArray()
		# z[z == orig_dem.get_nodata()] = np.nan    # this line probably needs improvement
		if resamp_method == 'nearest':
			print('resampling method = nearest')
			xx, yy = np.meshgrid(x, y)
			points = np.stack((np.reshape(xx, xx.size), np.reshape(yy, yy.size)), axis=-1)
			values = np.reshape(z, z.size)
			fun = NearestNDInterpolator(points, values)
			xnew = np.linspace(ulx, lrx - xres, resamp_ref_dem.get_x_size())
			ynew = np.linspace(uly, lry - yres, resamp_ref_dem.get_y_size())
			xxnew, yynew = np.meshgrid(xnew, ynew)
			znew = fun(xxnew, yynew)    # if the image is big, this may take a long time (much longer than linear approach)
		elif resamp_method == 'linear':
			nan_value = orig_dem.get_nodata()
			print('resampling method = interp2d - ' + resamp_method)
			fun = interp2d(x, y, z, kind=resamp_method, bounds_error=False, copy=False, fill_value=nan_value)
			xnew = np.linspace(ulx, lrx - xres, resamp_ref_dem.get_x_size())
			ynew = np.linspace(uly, lry - yres, resamp_ref_dem.get_y_size())
			znew = np.flipud(fun(xnew, ynew))    # I don't know why, but it seems f(xnew, ynew) is upside down.
			fun2 = interp2d(x, y, z != nan_value, kind=resamp_method, bounds_error=False, copy=False, fill_value=0)
			zmask = np.flipud(fun2(xnew, ynew))
			znew[zmask <= 0.999] = nan_value
		else:
			# This is deprecated...
			print('resampling method = griddata - ' + resamp_method)
			xx, yy = np.meshgrid(x, y)
			xx = xx.ravel()
			yy = yy.ravel()
			zz = z.ravel()
			realdata_pos = zz != orig_dem.get_nodata()
			xx = xx[realdata_pos]
			yy = yy[realdata_pos]
			zz = zz[realdata_pos]
			xnew = np.linspace(ulx, lrx - xres, resamp_ref_dem.get_x_size())
			ynew = np.linspace(uly, lry - yres, resamp_ref_dem.get_y_size())
			znew = griddata((xx, yy), zz, (xnew[None,:], ynew[:,None]), method='linear')
		del z
		gc.collect()
		return znew
	else:
		return np.ones_like(resamp_ref_dem.ReadAsArray()) * -9999.0