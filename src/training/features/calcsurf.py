import subprocess

def calcsurf(imagefilename,keypoints,size):
    '''
    Return SURF descriptors at the given locations and size.
    keypoints is an array of x,y points on the image.
    '''

    executable = './calcsurf'
    descriptors = []
    keypointfilename = 'tempkeypoints.csv'
    kpfile = open(keypointfilename,'w')
    for i in range(len(keypoints)):
        kpfile.write('%d %d %d\n' % (keypoints[i][0],keypoints[i][1],size))
    kpfile.close()
    
    for i in range(len(keypoints)):
        p = subprocess.Popen([executable, imagefilename, '%d' % (keypoints[i][0]), '%d' % (keypoints[i][1]), '%d' % (size)], stdout=subprocess.PIPE)
        out, err = p.communicate()
        descriptor = [float(s) for s in out.split()]
        descriptors.append(descriptor)
        
    return descriptors

