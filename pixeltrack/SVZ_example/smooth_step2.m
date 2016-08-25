function smooth_step2(step1_smoothed_file, crs)
%SMOOTH_STEP2 smoothes a geotiff file.
% based on the algorithm of Fahnestock et al. (2015): Landsat 8 image processing
% step1_smoothed_file: filename
% crs: 'EPSG:XXXX'
% version 1.0
% last modified by Whyjay Zheng, 2016 Mar 31

addpath('/13t1/whyj/Projects/Severnaya_Zemlya/PXtracking/Codes/')

[A, R] = geotiffread(step1_smoothed_file);

A(abs(A) < eps) = NaN;

idxm = [];
idxn = [];

for m = 2:(size(A, 1) - 1)
	for n = 2:(size(A, 2) - 1)
		if mod(m, 10) == 0 & n == 2
			disp(m)
		end
		masked = false;
		data_point = A(m, n);
		if isnan(data_point)
			masked = true;
			%disp('A')
		else
			judge_array = A(m - 1 : m + 1, n - 1 : n + 1);
			judge_array = [judge_array(1:4) judge_array(6:9)];
			judge_array = judge_array(~isnan(judge_array));
			if isempty(judge_array)
				masked = true;
				%disp('B')
			elseif numel(judge_array) == 1
				if abs(data_point - judge_array(1)) >= 1
					masked = true;
					%disp('C')
				end
			else
				if std(judge_array) <= 0.001
					masked = true;
					%disp('D')
				elseif abs(data_point - mean(judge_array)) >= 3 * std(judge_array)
					masked = true;
					%disp('E')
				elseif std(A(m - 1 : m + 1, n - 1 : n + 1)) >= 1
					masked = true;
					%disp('F')
				elseif max(judge_array) - min(judge_array) >= 1
					masked = true;
					%disp('G')
				end
			end	
		end
		if masked
			idxm(end + 1) = m;
			idxn(end + 1) = n;
		end
	end
end

for k = 1:length(idxm)
	A(idxm(k), idxn(k)) = NaN;
end

idxm2 = [];
idxn2 = [];


for m = 2:(size(A, 1) - 1)
	for n = 2:(size(A, 2) - 1)
		if mod(m, 10) == 0 & n == 2
			disp(m)
		end
		masked = false;
		judge_array = A(m - 1 : m + 1, n - 1 : n + 1);
		judge_array = [judge_array(1:4) judge_array(6:9)];
		judge_array = judge_array(~isnan(judge_array));
		if numel(judge_array) <= 2
			masked = true;
		end
		if masked
			idxm2(end + 1) = m;
			idxn2(end + 1) = n;
		end
	end
end

for k = 1:length(idxm2)
	A(idxm2(k), idxn2(k)) = NaN;
end


geotiffwrite(strrep(step1_smoothed_file, 'smooth1', 'smooth2'), A, R, 'CoordRefSysCode', crs)

B = A;
B(~all(isnan(A),2), ~all(isnan(A),1)) = inpaint_nans(double(A(~all(isnan(A),2), ~all(isnan(A),1))));

geotiffwrite(strrep(step1_smoothed_file, 'smooth1', 'smooth3'), B, R, 'CoordRefSysCode', crs)
