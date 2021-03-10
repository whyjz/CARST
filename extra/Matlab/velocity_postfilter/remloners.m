function [eastvel,northvel,iterations,loners]=remloners(eastvel,northvel,iterations,loners)
% function REMLONERS recursively removes lone pixels, defined as pixels
% with NaN values on 3 or more sides
%   eastvel  = east  velocities
%   northvel = north velocities
%   iterations = number of iterations so far
%   loners   = number of lone pixels

if loners > 0
    loners = 0;
    iterations = iterations+1;
    [xmax,ymax] = size(eastvel);
    
    for i = 2:(xmax-1)
        for j = 2:(ymax-1)
            if ~isnan(eastvel(i,j)) || ~isnan(northvel(i,j))
                borders = 4; % number of bordering pixels
            
                if isnan(eastvel(i,j+1)) || isnan(northvel(i,j+1))
                    borders = borders-1;
                end
                if isnan(eastvel(i,j-1)) || isnan(northvel(i,j-1))
                    borders = borders-1;
                end
                if isnan(eastvel(i+1,j)) || isnan(northvel(i+1,j))
                    borders = borders-1;
                end
                if isnan(eastvel(i-1,j)) || isnan(northvel(i-1,j))
                    borders = borders-1;
                end

                if borders < 2
                    % pixel i,j is a loner
                    eastvel(i,j) = NaN;
                    northvel(i,j) = NaN;
                    loners = loners+1;
                end
            end
        end
    end
    
    fprintf('succesfully removed %d lone pixels\n',loners);
    
    [eastvel,northvel,iterations,loners]=remloners(eastvel,northvel,iterations,loners);
    
end
end
                
                
                
                
                
                
                