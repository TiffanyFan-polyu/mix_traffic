
N=3;
a1=[108 116 482 -4];
Pbx=[1 0 0 0;
    0.16 0.84 0 0;
    0 0.16 0.84 0;
    0 0 0.4 0.6;]; %计算BX实际分布矩阵
DCbc=[1 0 0 0;
     0.16 1 0 0;
     0 0.16 1 0;
     0 0 0.4 1;]; %计算BXdouble counting矩阵
b1=a1*Pbx^N; %计算BX实际分布
c1=a1*Pbx^(N-1)*DCbc; %计算BXdouble counting


a2=[94 107 -269 402];
Pay=[0.36 0.64 0 0;
     0 0.36 0.64 0;
     0 0 0.71 0.29;
     0 0 0 1;];%计算AY实际分布矩阵
DCay=[1 0.64 0 0;
      0 1 0.64 0;
      0 0 1 0.29
      0 0 0 1;];%计算AY double counting矩阵
b2=a2*Pay^N;
c2=a2*Pay^(N-1)*DCay;

b=b1+b2; % total distribution
c=c1+c2; % total distribution of double counting