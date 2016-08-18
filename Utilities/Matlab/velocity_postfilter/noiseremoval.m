function [eastvel,northvel,iterations,span,numdif,noisy] = noiseremoval(velmax, tol, numdif, ew_grd, ns_grd)

% noiseremoval.m
% removes noise from east and west velocity .grd files

% Initializations...

% Juneau ALOS
%velmax = 2.0; % m/day
%tol = 0.2; % required tolerance, 0.1 means within 10% of velmax
%numdif = 3; % number of pixels within tol required

% NovZ dh/dt
%velmax = 30.0; % m/day
%tol = 0.2; % required tolerance, 0.1 means within 10% of velmax
%numdif = 2; % number of pixels within tol required

% NovZ 1-year Landsat
%velmax = 2.0; % m/day
%tol = 0.2; % required tolerance, 0.1 means within 10% of velmax
%numdif = 3; % number of pixels within tol required

% NovZ months Landsat
%velmax = 4.0; % m/day
%tol = 0.2; % required tolerance, 0.1 means within 10% of velmax
%numdif = 2; % number of pixels within tol required

% NovZ INO
%velmax = 10.0; % m/day
%tol = 0.3; % required tolerance, 0.1 means within 10% of velmax
%numdif = 3; % number of pixels within tol required

% NovZ INO Winter/Spring
%velmax = 7.0; % m/day
%tol = 0.3; % required tolerance, 0.1 means within 10% of velmax
%numdif = 3; % number of pixels within tol required

% NovZ 1-day ERS
%velmax = 2000.0; % m/day
%tol = 0.4; % required tolerance, 0.1 means within 10% of velmax
%numdif = 2; % number of pixels within tol required

span = velmax*tol; % +- range of variations between "similar" pixels

% Read GMT files
[~,~,eastvel]  = grdread2(ew_grd);
[x,y,northvel] = grdread2(ns_grd);


% Remove unreasonably fast velocities
disp('Removing unreasonably fast velocities...');
for i = 1:length(y)
    for j = 1:length(x)
        if (abs(eastvel(i,j))>velmax) || (abs(northvel(i,j))>velmax)
            eastvel(i,j) = NaN;
            northvel(i,j)= NaN;
        end
    end
end

% Remove edges
disp('Removing edges...');
eastvel(1,:) = NaN; northvel(1,:) = NaN;
eastvel(:,1) = NaN; northvel(:,1) = NaN;
eastvel(length(y),:) = NaN; northvel(length(y),:) = NaN;
eastvel(:,length(x)) = NaN; northvel(:,length(x)) = NaN;

% Remove lone pixels recursively
disp('Removing lone pixels recursively...')
loners = 1;
iterations = 0;
[eastvel,northvel,iterations]=remloners(eastvel,northvel,iterations,loners);
fprintf('noiseremoval.m ran through %d iterations of remloners.m\n',iterations);

% Remove remaining noise
disp('Removing remaining noise...')
noisy = 1;
iterations = 0;
[eastvel,northvel,iterations]=remnoise(eastvel,northvel,iterations,span,numdif,noisy);
fprintf('noiseremoval.m ran through %d iterations of remnoise.m\n',iterations);

% Write GMT files
grdwrite2(x,y,eastvel,strrep(ew_grd,'.grd','_filt.grd'));
grdwrite2(x,y,northvel,strrep(ns_grd,'.grd','_filt.grd'));

disp('Finished successfully')

end
