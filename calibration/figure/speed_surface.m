% X1 is the first variables; X2 is the second variables
clear
clc
addpath(genpath('D:\FTT\A-reproducible-approach-to-merging-behavior-analysis-based-on-High-Definition-Map-main\calibration\scene\output'));%add the filepath

x1=60:60:14365; %time(uncertain)
x2=-100:10:160; % position
n1=length(x1);
n2=length(x2);
n12=n1*n2;


%  Z1=zeros(n1,n2);
%     for k2=1:1:n2
%         Z1(:,k2)=csvread('1.csv',(k2-1)*n1,2,[(k2-1)*n1,2,k2*n1-1,2]);    
%     
%     end
% %[X,Y]=meshgrid(x2,x1);


Y1=csvread('onramp_default.csv',0,0,[0,0,n12-1,0]); %add the file name
Y2=csvread('onramp_default.csv',0,1,[0,1,n12-1,1]);   
Y2=Y2*10;
Z1=csvread('onramp_default.csv',0,2,[0,2,n12-1,2]);   

    
% [X,Y,Z2]=griddata(Y1,Y2,Z1,linspace(min(Y1),max(Y1),25)',linspace(min(Y2),max(Y2),25),'cubic');
% [X3,Y3,Z3]=griddata(Y1,Y2,Z1,linspace(min(Y1),max(Y1),25)',linspace(min(Y2),max(Y2),25),'cubic');
% 
[X,Y,Z2]=griddata(Y1,Y2,Z1,linspace(min(Y1),max(Y1))',linspace(min(Y2),max(Y2)),'cubic');
[X3,Y3,Z3]=griddata(Y1,Y2,Z1,linspace(min(Y1),max(Y1))',linspace(min(Y2),max(Y2)),'cubic');

% figure;
% pcolor(X,Y,Z1);
% shading interp           %???? 
% contourf(X,Y,Z1)          %???? figure,contourf(X,Y,Z)
% mesh(X,Y,Z1)              %????


y=-100:10:160;
figure  
pcolor(X,Y,Z2);
shading interp
hold on
contourf(X,Y,Z2,'linestyle','none');

xlabel('Time (s)');
ylabel('Distance (m)');
zlabel('Speed (m/s)');
hold off

% figure
% y=-180:10:500;
% surf(X,Y,Z2);
% shading interp
% hold on
% contourf(X3,Y3,Z3,4,'linestyle','-');
% shading interp
% C1=parula(100);
% C2=flipud(C1);
% C2(85:100,:)=[];
% colormap(C2);
% %mesh(X,Y,Z2);
% xlabel('Time (s)');
% ylabel('Distance (m)');
% zlabel('Speed (mph)');
% hold off