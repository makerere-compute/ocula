kneg = 1;
kpos = 1;

%Xneg = dlmread('negdescriptors.csv',' ');
%Xpos = dlmread('posdescriptors.csv',' ');

xdim = size(Xneg,2);

if kneg>1
[Wneg,Mneg,Vneg,Lneg] = EM_GM(Xneg(1:15000,1:128),kneg,2,1);
else
Wneg = 1;
Mneg = mean(Xneg);
Mneg = Mneg';
Vneg= cov(Xneg);
end

if kpos>1
[Wpos,Mpos,Vpos,Lpos] = EM_GM(Xpos(1:5000,1:128),kpos,2,1);
else
Wpos = 1;
Mpos = mean(Xpos);
Mpos = Mpos';
Vpos= cov(Xpos);
end
classes = zeros(kneg+kpos,1);
classes(1:kpos) = 1;

weights = [Wpos Wneg];

means = [Mpos Mneg];

covs = zeros(xdim,xdim*(kneg+kpos));
for i=1:kpos
    covs(:,(i-1)*xdim+1:i*xdim) = Vpos(:,:,i);
end
for i=1:kneg
    covs(:,(i-1+kpos)*xdim+1:(i+kpos)*xdim) = Vneg(:,:,i);
end

outdir = '../../data/params/';
dlmwrite([outdir 'classes.txt'],classes,' ');
dlmwrite([outdir 'weights.txt'],weights,' ');
dlmwrite([outdir 'means.txt'],means,' ');
dlmwrite([outdir 'covs.txt'],covs,' ');
