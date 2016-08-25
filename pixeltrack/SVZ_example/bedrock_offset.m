function [xoff, yoff] = bedrock_offset(ampcoroff_file)
%BEDROCK_OFFSET makes statistics about the bedrock pixel tracking.
% ampcoroff_file: filename
% version 1.01
% first created modified by Whyjay Zheng, 2016 Apr 11
% last modified by Whyjay Zheng, 2016 Apr 22

output_filename = 'bedrock_statistics.txt';

ampcor = load(ampcoroff_file);
xoff = ampcor(:, 2);
yoff = ampcor(:, 4);

% inputfile1 = '../setup_pixel_tracking.bash';
% inputfile2 = '../smoothing.bash';

% ==== parsing arguments from input files ====

% inf1 = fopen(inputfile1, 'r');
% inf1_cell = textscan(inf1, '%s');
% arguments = textscan(inf1_cell{1}{33}, '%s', 'delimiter', '''');
% input_prefix = arguments{1}{2};
% arguments = textscan(inf1_cell{1}{35}, '%s', 'delimiter', '''');
% datedelta = arguments{1}{2};

% inf2 = fopen(inputfile2, 'r');
% inf2_cell = textscan(inf2, '%s');
% arguments = textscan(inf2_cell{1}{13}, '%s', 'delimiter', '"');
% snr_threshold_sqrt = arguments{1}{2};

% ==== trimming and calculate robust estimation of mean and std ====

trimxoff = trim_by_mad(xoff);
trimyoff = trim_by_mad(yoff);

% ==== making output file ====

f = fopen(output_filename, 'w');
fprintf(f, 'x_median            = %6.3f\n', median(trimxoff));
fprintf(f, 'y_median            = %6.3f\n', median(trimyoff));
fprintf(f, 'x_std               = %6.3f\n', std(trimxoff));
fprintf(f, 'y_std               = %6.3f\n', std(trimyoff));
fprintf(f, 'x_skewness          = %6.3f\n', skewness(trimxoff));
fprintf(f, 'y_skewness          = %6.3f\n', skewness(trimyoff));
fprintf(f, 'x_kurtosis          = %6.3f\n', kurtosis(trimxoff));
fprintf(f, 'y_kurtosis          = %6.3f\n', kurtosis(trimyoff));
% fprintf(f, 'datedelta          = %s\n', datedelta );
% fprintf(f, 'input_prefix       = %s\n', input_prefix );
% fprintf(f, 'snr_threshold_sqrt = %s\n', snr_threshold_sqrt );
fclose(f);

% ==== making histogram ====

xbins = linspace(min(xoff), max(xoff), 200);
ybins = linspace(min(yoff), max(yoff), 200);
subplot(2, 1, 1)
hist(xoff, xbins);
hx1 = findobj(gca,'Type','patch');
hold on
hist(trimxoff, xbins);
hx2 = setdiff(findobj(gca,'Type','patch'), hx1);
xlim([min(xoff), max(xoff)])
title('bedrock offset histogram - x')
subplot(2, 1, 2)
hist(yoff, ybins);
hy1 = findobj(gca,'Type','patch');
xlim([min(yoff), max(yoff)])
hold on
hist(trimyoff, ybins);
hy2 = setdiff(findobj(gca,'Type','patch'), hy1);
title('bedrock offset histogram - y')

set([hx1 hy1], 'FaceColor', [0.95 0.25 0.1], 'EdgeColor', [0.95 0.25 0.1])
set([hx2 hy2], 'FaceColor', [0.1 0.25 0.95], 'EdgeColor', [0.1 0.25 0.95])
print -dpng bedrock_statistics.png

function trimx = trim_by_mad(x)

	nth = 3;
	madd = @(x) 1.4826 * median(abs(x - median(x)));
	lbound = median(x) - nth * madd(x);
	ubound = median(x) + nth * madd(x);
	trimx = x(x > lbound & x < ubound);

