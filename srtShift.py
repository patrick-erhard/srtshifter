#!/usr/bin/python
#
# This scripts shifts subtitle .srt files, with a delay
# linearly interpolated between initialDelay (first subtitle)
# and finalDelay (last subtitle).
# A positive value advances the subtitles, a negative one delays them.
#
import argparse
#----------------------------------------------------------------------
class Time:
    def __init__(self,v):
        if type(v) is str:
            self.str=v
            self.val=self.num(v)
        elif type(v) is float:
            self.val=v
            self.str=self.fmt(v)
        else:
            print "No argument accepted, except string or float"
            raise TypeError
            
    def fmt(self,v):
        v=(round(1000.*v))/1000.
        minutes=int(v/60.)
        v-=(60.*minutes)
        hours=int(minutes/60.)
        minutes-=(60*hours)
        mantissa=v-int(v)
        return "{:02d}:{:02d}:{:02d},{:03d}".format(hours,minutes,int(v),int(mantissa*1000))

    def num(self,v):
        lv=v.split(':')
        hours=int(lv[0])
        minutes=int(lv[1])
        [sec,msec]=lv[-1].split(',')
        msec+="000"
        return 3600.*hours+60.*minutes+int(sec)+(0.001*int(msec[:3]))

    def __add__(self,other):
        if isinstance(other,Time):
            return Time(self.val+other.val)
        else:
            return Time(self.val+other)
#----------------------------------------------------------------------      
class srtFiles:
    def __init__(self,delay1=None,delay2=None,fname=None):
        if fname is None:
            print "Input file name missing!"
            raise NameError
        if fname.count(".srt") == 1:
            self.fileName=fname
        else:
            self.fileName=fname+".srt"
        self.File=open(self.fileName,'r')
        if delay1 is None: delay1=0.0
        self.initialDelay=delay1
        if delay2 is None:
            self.finalDelay=delay1
        else:
            self.finalDelay=delay2
        
    def read(self):
        zzz=self.File.readlines()
        self.endl=zzz[0][1:]
        self.ALL=[z[:-len(self.endl)] for z in zzz]
        self.INDEX=[]
        for (i,z) in enumerate(self.ALL):
            if z == '': self.INDEX.append(i)
        self.DATE=[self.ALL[1]]+[self.ALL[i+2] for i in self.INDEX[:-1]] # skip last one (tagged 9999)
        self.TEXT=[self.ALL[2:self.INDEX[0]]]+[self.ALL[self.INDEX[i]+3:self.INDEX[i+1]] for i in range(len(self.INDEX)-1)]
        self.QUEUE=self.ALL[1+self.INDEX[-1]:]
        return

    def dump(self):
        outfile=open(self.fileName[:-4]+'_Shifted.srt','w')
        for (i,d) in enumerate(self.DATE):
            outfile.write("{:d}".format(i+1)+self.endl)
            outfile.write("{:s}".format(d)+self.endl)
            for z in self.TEXT[i]:
                outfile.write("{:s}".format(z)+self.endl)
            outfile.write(self.endl)
        for z in self.QUEUE:
            outfile.write("{:s}".format(z)+self.endl)
        outfile.flush()
        return

    def shift(self, sep=" --> "):
        date1,date2 = self.DATE[0],self.DATE[-1]
        t1,t2 = date1.split(sep)[0],date2.split(sep)[0]
        TINI,TEND = Time(t1).val,Time(t2).val
        DT=TEND-TINI
        for k,dt in enumerate(self.DATE):
            d1,d2 = dt.split(sep)
            dd1,dd2 = Time(d1).val,Time(d2).val
            SPENT=(dd1-TINI)/DT
            currentDelay=(1.-SPENT)*self.initialDelay+SPENT*self.finalDelay
            dd1-=currentDelay
            dd2-=currentDelay
            self.DATE[k]=Time(dd1).str+sep+Time(dd2).str
        return
#
#=============  MAIN ROUTINE ==================================
#
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--initialDelay", type=float,
                    help="initial delay, in seconds : a positive REAL NUMBER (e.g. 5.0 for 5 seconds) advances subtitles, a negative one (e.g. -5.0) delays them")
parser.add_argument("-f", "--finalDelay", type=float,
                    help="final delay, in seconds : a positive REAL NUMBER (e.g. 9.0 for 9 seconds) advances subtitles, a negative one (e.g. -9.0) delays them")
parser.add_argument("srtFile", type=str,
                    help="name of subtitle srt file (without type '.srt')")
args = parser.parse_args()

subtitles=srtFiles(delay1=args.initialDelay,delay2=args.finalDelay,fname=args.srtFile)
subtitles.read()
subtitles.shift()
subtitles.dump()
#
#================================================================
#
