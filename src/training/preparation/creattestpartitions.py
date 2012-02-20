countfile = open('counts.csv','r')
ntestimages = 800
partitionsize=80
npatchesperimage = 1200
npartitions = ntestimages/partitionsize
outdir = '../../data'

for ipartition in range(npartitions):
    filelist = []
    objectcount = 0
    outfile = open('%s/testpartition_%.2d.txt' % (outdir,ipartition),'w')
    for ifile in range(partitionsize):
        s1 = countfile.readline()
        s2 = s1.replace('"','').replace(';','').replace('\n','').split()
        filelist.append(s2[0])
        objectcount += int(s2[1])
    posnegratio = (1.0*objectcount)/(partitionsize*npatchesperimage)
    outfile.write('%.4f\n' % (posnegratio))
    for ifile in range(partitionsize):
        outfile.write('%s\n' % (filelist[ifile]))
    outfile.close()
countfile.close()
