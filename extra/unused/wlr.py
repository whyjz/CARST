# This script archives old code for wlr_corefun in libdhdt.py.

# ============ Using Cook's Distance ============
		# cookd     = ri2 / (p_num * mse) * (h / (1 - h) ** 2)    # Cook's Distance
		# goodpoint = cookd < 4 / x.size                          # Bollen, Kenneth A.; Jackman, Robert W. (1990) (see wikipedia)
		# # xnew = x[goodpoint]
		# # ynew = y[goodpoint]
		# # yenew = ye[goodpoint]
		# # wnew = [1 / k for k in yenew]
		# if np.all(goodpoint):
		# 	slope = p[0] * 365.25
		# 	slope_err = np.sqrt(cov_m[0, 0]) * 365.25
		# 	count = x.size
		# 	if resid > 100000:
		# 		print(x,y,ye,cookd,goodpoint)
		# 	return slope, slope_err, resid, count
		# else:
		# 	xnew = x[goodpoint]
		# 	ynew = y[goodpoint]
		# 	yenew = ye[goodpoint]
		# 	return wlr_corefun(xnew, ynew, yenew)

	# =========== Old function ===========
	# if xnew.size > 4:
	# 	p, c            = np.polyfit(xnew, ynew, 1, w=wnew, cov=True)
	# 	_, res, _, _, _ = np.polyfit(xnew, ynew, 1, w=wnew, full=True)
	# 	residual = np.sum((np.polyval(p, xnew) - ynew) ** 2)
	# 	cov_m = c * (len(w) - 4) / res
	# 	error =  np.sqrt(cov_m[0, 0])
	# 	slope = p[0] * 365.25
	# 	slope_err = np.sqrt(cov_m[0, 0]) * 365.25
	# else:
	# 	error = -9999.0
	# 	slope = -9999.0
	# 	slope_err = -9999.0

	# case = 0
	# w = [1 / k for k in ye]
	# if len(x) == 4:
	# 	case = 1
	# 	# This is to avoid dividing by zero when N = 4 and to give us a better error estimate
	# 	x  = np.append(x,   x[-1])
	# 	y  = np.append(y,   y[-1])
	# 	ye = np.append(ye, ye[-1])
	# 	w  = np.append(w, sys.float_info.epsilon)
	# elif len(x) == 3:
	# 	case = 2
	# 	# This is to avoid negative Cd^2 when N = 3 and to give us a better error estimate
	# 	x  = np.append(x,  [x[-1],  x[-1]])
	# 	y  = np.append(y,  [y[-1],  y[-1]])
	# 	ye = np.append(ye, [ye[-1], ye[-1]])
	# 	w  = np.append(w,  [sys.float_info.epsilon, sys.float_info.epsilon])
	# p, c            = np.polyfit(x, y, 1, w=w, cov=True)
	# _, res, _, _, _ = np.polyfit(x, y, 1, w=w, full=True)
	# # where c is the covariance matrix of p -> c[0, 0] is the variance estimate of the slope.
	# # what we want is ({G_w}^T G_w)^{-1}, which is equal to c * (N - m - 2) / res
	# cov_m = c * (len(w) - 4) / res
	# slope = p[0] * 365.25
	# slope_err = np.sqrt(cov_m[0, 0]) * 365.25
	# # slope_error_arr[m, n] = np.sqrt(c[0, 0]) * 365.25
	# # ./point_TS_ver2-2_linreg.py:^^^^^^^^: RuntimeWarning: invalid value encountered in sqrt
	# # /data/whyj/Software/anaconda3/lib/python3.5/site-packages/numpy/lib/polynomial.py:606: RuntimeWarning: divide by zero encountered in true_divide
	# # fac = resids / (len(x) - order - 2.0)
	# if case == 0:
	# 	residual = np.sum((np.polyval(p, x) - y) ** 2)
	# elif case == 1:
	# 	residual = np.sum((np.polyval(p, x[:-1]) - y[:-1]) ** 2)
	# elif case == 2:
	# 	residual = np.sum((np.polyval(p, x[:-2]) - y[:-2]) ** 2)
	# return slope, slope_err, residual