kneg = 10;
kpos = 10;

Xn = dlmread('negmoments.csv',' ');
Xp = dlmread('posmoments.csv',' ');

Xneg = Xn(find(Xn(:,1)>0),:);
Xpos = Xp(find(Xp(:,1)>0),:);

xdim = size(Xneg,2);

if kneg>1
[Wneg,Mneg,Vneg,Lneg] = EM_GM(Xneg,kneg,2,5);
else
Wneg = 1;
Mneg = mean(Xneg);
Mneg = Mneg';
Vneg= cov(Xneg);
end

if kpos>1
[Wpos,Mpos,Vpos,Lpos] = EM_GM(Xpos,kpos,2,5);
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
dlmwrite([outdir 'moments_classes.txt'],classes,' ');
dlmwrite([outdir 'moments_weights.txt'],weights,' ');
dlmwrite([outdir 'moments_means.txt'],means,' ');
dlmwrite([outdir 'moments_covs.txt'],covs,' ');
