% Matlab script
% making glacier meeting 2016/02/19 plots
% by WhyJ, 2016/2/18

a = load('/data/whyj/Projects/Franz_Josef_Land/dHdt/Regression/Hooker/grdtrack_output.txt');
for m = 4:8
wv_diff{m-3} = a(:,m) - a(:,3);
wv_diff{m-3} = wv_diff{m-3}(~isnan(wv_diff{m-3}));
end
for m = 4:8
   wv_diff2(:,m-3) = a(:,m) - a(:,3);
end
for m = 1:5
    figure
    hist(wv_diff{m},-2:0.1:2)
end
% ---- figure 1
figure
hist(wv_diff{3},-10:0.1:30)
xlim([-10.5,27])
ylim([0,17])
title('tipycal distribution')
xlabel('Aligned WV - ICESat')
title('tipycal distribution: 13APR18WV01DEM1')
set(gca,'FontSize',14)
set(gca,'FontSize',16)
set(gca,'FontSize',18)
xlabel('Aligned WV - ICESat (m)')
% ---- figure 2
figure
boxplot(wv_diff2,'labels',{'[11AUG16 N=225]', '[12JUL20 N=417]', '[13APR18 N=224]', '[13APR19 N=236]', '[14APR02 N=223]'}, 'whisker', 1.5)
ylim([-2,2])
ylabel('Aligned WV - ICESat (m)')
title('Hooker Island')
grid on
