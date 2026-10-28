import numpy as np, subprocess, sys, scipy.signal as sg, scipy.io.wavfile as wf
src, out, start, dur = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
sr=22050
raw=subprocess.run(["ffmpeg","-v","error","-ss",str(start),"-t",str(dur),"-i",src,"-f","s16le","-ac","2","-ar",str(sr),"-"],capture_output=True).stdout
x=np.frombuffer(raw,np.int16).astype(np.float32).reshape(-1,2)/32768
L,R=x[:,0],x[:,1]; mid=(L+R)/2; side=(L-R)/2
f,t,Z=sg.stft(mid,sr,nperseg=2048,noverlap=1536)
S=np.abs(Z)
# remove side-correlated (wide) energy: soft mask from side ratio
_,_,Zs=sg.stft(side,sr,nperseg=2048,noverlap=1536); Ss=np.abs(Zs)
center=np.clip(1-(Ss/(S+1e-6))**2*1.5,0,1)
# REPET-SIM: similarity matrix on log-mag
Fv=np.log1p(S[:400]); Fv=Fv/ (np.linalg.norm(Fv,axis=0,keepdims=True)+1e-9)
n=S.shape[1]; hop=512/sr; mind=int(1.0/hop); K=40
bg=np.zeros_like(S)
for i in range(0,n,1):
    sim=Fv[:,i]@Fv
    lo,hi=max(0,i-mind),min(n,i+mind); sim[lo:hi]=-1
    idx=np.argpartition(-sim,K)[:K]
    bg[:,i]=np.median(S[:,idx],axis=1)
bg=np.minimum(bg,S)
mask=(S-bg)/(S+1e-9)
mask=np.clip(mask,0,1)**1.3*center
# keep vocal band
band=((f>120)&(f<7000)).astype(float)[:,None]
_,v=sg.istft(Z*mask*band,sr,nperseg=2048,noverlap=1536)
v=v/ (np.max(np.abs(v))+1e-9)*0.9
wf.write(out,sr,(v*32767).astype(np.int16))
print('ok',n)
