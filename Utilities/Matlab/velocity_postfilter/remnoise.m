function [eastvel,northvel,iterations,span,numdif,noisy] = remnoise(eastvel,northvel,iterations,span,numdif,noisy)
% function REMNOISE recursively removes remaining noise
% noise is defined as pixels which have less than some required percentage
% of neighboring pixels which are within a specified tolerance
%   eastvel  = east  velocities
%   northvel = north velocities
%   iterations = number of times remnoise.m has been run
%   span   = +- range of velocities defined as "similar" enough
%   numdif = number of pixels within tol required
%   noisy  = number of noisy pixels found and removed during each iteration


if noisy > 0
    noisy = 0;
    iterations = iterations+1;
    [xmax,ymax] = size(eastvel);
    remlater = zeros(xmax,ymax);
    
    for i = 2:(xmax-1)
        for j = 2:(ymax-1)
            if ~isnan(eastvel(i,j)) || ~isnan(northvel(i,j))
                
                similarities = 0; % number of similar bordering pixels
            
                if abs(abs(eastvel(i,j))-abs(eastvel(i,j+1))) < span &&...
                   abs(abs(northvel(i,j))-abs(northvel(i,j+1))) < span
                    similarities = similarities+1;
                end
                if abs(abs(eastvel(i,j))-abs(eastvel(i,j-1))) < span &&...
                   abs(abs(northvel(i,j))-abs(northvel(i,j-1))) < span
                    similarities = similarities+1;
                end
                if abs(abs(eastvel(i,j))-abs(eastvel(i+1,j))) < span &&...
                   abs(abs(northvel(i,j))-abs(northvel(i+1,j))) < span
                    similarities = similarities+1;
                end
                if abs(abs(eastvel(i,j))-abs(eastvel(i-1,j))) < span &&...
                   abs(abs(northvel(i,j))-abs(northvel(i-1,j))) < span
                    similarities = similarities+1;
                end
                if abs(abs(eastvel(i,j))-abs(eastvel(i+1,j+1))) < span &&...
                   abs(abs(northvel(i,j))-abs(northvel(i+1,j+1))) < span
                    similarities = similarities+1;
                end
                if abs(abs(eastvel(i,j))-abs(eastvel(i-1,j+1))) < span &&...
                   abs(abs(northvel(i,j))-abs(northvel(i-1,j+1))) < span
                    similarities = similarities+1;
                end
                if abs(abs(eastvel(i,j))-abs(eastvel(i+1,j-1))) < span &&...
                   abs(abs(northvel(i,j))-abs(northvel(i+1,j-1))) < span
                    similarities = similarities+1;
                end
                if abs(abs(eastvel(i,j))-abs(eastvel(i-1,j-1))) < span &&...
                   abs(abs(northvel(i,j))-abs(northvel(i-1,j-1))) < span
                    similarities = similarities+1;
                end
                

                if similarities <= numdif
                    % pixel i,j is noisy
                    remlater(i,j) = 1;
                    noisy = noisy+1;
                end
                
            end
        end
    end
    
    for i = 2:(xmax-1)
        for j = 2:(ymax-1)
            if remlater(i,j)
                eastvel(i,j)  = NaN;
                northvel(i,j) = NaN;
            end
        end
    end
    
    fprintf('succesfully removed %d noisy pixels\n',noisy);
    
    [eastvel,northvel,iterations,span,numdif,noisy] = remnoise(eastvel,northvel,iterations,span,numdif,noisy);
    
end
end

