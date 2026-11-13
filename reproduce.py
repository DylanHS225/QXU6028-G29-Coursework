#!/usr/bin/env python3
"""Recompute the regular G29 report and all data figures from original inputs."""
from pathlib import Path
import hashlib
import json
import subprocess
import os
import tempfile
import sys
import platform
from datetime import datetime, timezone
import numpy as np
import pandas as pd
os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir())/'qxu6028-matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import MaxNLocator, ScalarFormatter
import course_methods as cm

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data' / 'regular_G29'
OUT = ROOT / 'figures'
try:
    font_manager.findfont('Arial',fallback_to_default=False)
    FIGURE_FONT='Arial'
except ValueError:
    FIGURE_FONT='DejaVu Sans'
    print('Arial is unavailable: using DejaVu Sans for figures; numerical results are unaffected.')
BLUE, ORANGE, GREY = '#235987', '#c66a24', '#62676d'
plt.rcParams.update({'font.family': FIGURE_FONT, 'font.size': 10,
                     'mathtext.fontset':'custom','mathtext.rm':FIGURE_FONT,
                     'mathtext.it':FIGURE_FONT+':italic','mathtext.bf':FIGURE_FONT+':bold',
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.labelsize': 10, 'legend.fontsize': 9,
                     'savefig.dpi': 300, 'axes.titlesize': 11})


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def save_figure(fig, name):
    for suffix in ['png', 'pdf']:
        metadata={'CreationDate': None, 'ModDate': None} if suffix=='pdf' else {}
        fig.savefig(OUT / (name + '.' + suffix), bbox_inches='tight', metadata=metadata)
    plt.close(fig)


def verify_data(folder):
    manifest = cm.read_json(folder / 'manifest.json')
    for entry in manifest['files']:
        p = folder / entry['name']
        assert hashlib.sha256(p.read_bytes()).hexdigest() == entry['sha256'], p.name
    return manifest


def counts(ef, temp, slope, points=20001):
    values = []
    for lower in [0.0, ef]:
        energy = np.linspace(lower, cm.EMAX, points)
        values.append(cm.NA * np.trapezoid(slope * energy * cm.fermi(energy, ef, temp), energy))
    return np.array(values)


def crossing(target, temp, slope):
    lower, upper = 0.0, 0.25
    for _ in range(45):
        middle = (lower + upper) / 2
        nb, nf = counts(middle, temp, slope)
        if nb / nf < target:
            lower = middle
        else:
            upper = middle
    return (lower + upper) / 2


def analyse_l1():
    par = cm.read_json(DATA / 'L1_params.json')
    data = pd.read_csv(DATA / 'L1_data.csv')
    temp, slope, ef_op, rho = (par[k] for k in ['T', 'c', 'EF_op_eV', 'rho_ohm_sq'])
    ef = np.linspace(0, data.EF_eV.max(), 501)
    nb, nf = np.array([counts(x, temp, slope) for x in ef]).T
    op_b, op_f = counts(ef_op, temp, slope)
    closed = cm.NA*slope*cm.KB*temp*(ef*np.log(2)+np.pi**2*cm.KB*temp/12)
    relative_error = np.max(np.abs(nf/closed-1))
    gate = {str(x): float(np.prod(counts(x,temp,slope)**[1,-1])) for x in [0, .073, .1, .2]}
    cross = [crossing(v, temp, slope) for v in [2,4]]
    table_counts = np.array([counts(x,temp,slope) for x in data.EF_eV])
    supplied_error = np.max(np.abs(table_counts[:,0]/data.n_band_cm2-1))
    refined = counts(ef_op,temp,slope,40001)
    assert relative_error < 1e-5
    assert abs(gate['0']-1) < 1e-12 and np.all(np.diff(nb/nf)>0)
    summary = dict(temperature_K=temp, slope=slope, operating_EF_eV=ef_op, rho_ohm_sq=rho,
                   n_band_cm2=float(op_b), n_fermi_cm2=float(op_f), correction=float(op_b/op_f),
                   mobility_band=float(1/(cm.QE*op_b*rho)), mobility_corrected=float(1/(cm.QE*op_f*rho)),
                   crossings_eV=cross, gates=gate, max_closed_form_relative_error=float(relative_error),
                   supplied_count_relative_error=float(supplied_error),
                   doubled_grid_change=float(np.max(np.abs(refined/[op_b,op_f]-1))))
    fig, axes = plt.subplots(1,2,figsize=(10,3.65),layout='constrained')
    axes[0].plot(ef,nb/1e12,color=BLUE,label='Band-edge model')
    axes[0].scatter(data.EF_eV,data.n_band_cm2/1e12,color=BLUE,s=14,label='Supplied counts',zorder=4)
    axes[0].plot(ef,nf/1e12,color=ORANGE,ls='--',label='Fermi-referenced model')
    axes[0].set(xlabel='$E_F$ (eV)',ylabel='Carrier density ($10^{12}$ cm$^{-2}$)',title='(a) Carrier counting',ylim=(0,None))
    axes[0].legend(loc='upper left')
    axes[1].plot(ef,nb/nf,color=BLUE)
    axes[1].scatter(data.EF_eV,data.n_band_cm2/table_counts[:,1],s=15,color=BLUE)
    for target,x in zip([2,4],cross):
        axes[1].axhline(target,color='0.75',ls=':',lw=.8)
        axes[1].scatter(x,target,color=ORANGE,zorder=4)
        axes[1].annotate(f'{x:.4f} eV',(x,target),xytext=(6,-22 if target==2 else 7),textcoords='offset points',fontsize=9)
    axes[1].scatter(ef_op,op_b/op_f,marker='*',s=95,color='black',zorder=5,label=f'Operating point {ef_op:.5f} eV')
    axes[1].set(xlabel='$E_F$ (eV)',ylabel='$C=n_B/n_F$',title='(b) Correction factor',ylim=(.8,6.8))
    axes[1].legend(loc='upper left')
    save_figure(fig,'fig2_l1')
    return cm.l1(DATA), summary


def analyse_l2():
    index,reps,temp=cm.l2_repeats(DATA)
    grid,gaps,curves=cm.model_library(temp)
    mean=reps.mean(axis=1)
    selected,best,rms,trajectory=cm.fit_l2(mean,grid,gaps,curves)
    normal=cm.normalise(mean)
    distances=((normal[:,None,:]-curves[selected][None,:,:])**2).sum(axis=2)
    fitted=curves[selected][distances.argmin(axis=1)]
    rng=np.random.default_rng(cm.SEED_L2)
    boot_gap,boot_ef=[],[]
    for _ in range(200):
        sample=reps[np.arange(len(index)),rng.integers(0,3,len(index))]
        choice,_,_,ef=cm.fit_l2(sample,grid,gaps,curves)
        boot_gap.append(gaps[choice]); boot_ef.append(ef)
    q=np.percentile(boot_gap,[16,50,84])
    efq=np.percentile(boot_ef,[16,50,84],axis=0)
    crossings=np.flatnonzero(mean[:-1,0]*mean[1:,0]<0)
    assert len(crossings)>0 and len(trajectory)==len(index)
    summary=dict(n_measurements=len(index),temperature_K=temp,gap_kT=float(gaps[selected]),
                 gap_meV=float(gaps[selected]*cm.KB*temp*1000),gap_quantiles_kT=q.tolist(),
                 gap_selection_fraction=float(np.mean(np.array(boot_gap)>0)),
                 rms_cone=float(rms[0]),rms_hard_gap=float(rms[best]),best_hard_gap_kT=float(gaps[best]),
                 fractional_improvement=float(1-rms[best]/rms[0]),
                 neutrality_brackets=[[int(index[k]),int(index[k+1])] for k in crossings],
                 ef_start_eV=float(trajectory[0]),ef_end_eV=float(trajectory[-1]),
                 ef_min_eV=float(trajectory.min()),ef_max_eV=float(trajectory.max()),
                 max_trajectory_interval_eV=float(np.max(efq[2]-efq[0])))
    pd.DataFrame(dict(index=index,EF_eV=trajectory,EF_p16_eV=efq[0],EF_p84_eV=efq[2],
                      RH_normalised=normal[:,0],Rs_normalised=normal[:,1],
                      RH_residual=normal[:,0]-fitted[:,0],Rs_residual=normal[:,1]-fitted[:,1])).to_csv(ROOT/'evidence/l2_fit.csv',index=False)
    pd.DataFrame({'Eg_kT':boot_gap}).to_csv(ROOT/'evidence/l2_bootstrap.csv',index=False)
    fig,axes=plt.subplots(2,2,figsize=(10,6.8),layout='constrained')
    for ax,j,label in [(axes[0,0],0,'Hall resistance'),(axes[0,1],1,'Sheet resistance')]:
        ax.plot(grid/(cm.KB*temp),curves[best,:,j],color=GREY,ls=':',label='Best hard-gap candidate')
        ax.plot(grid/(cm.KB*temp),curves[selected,:,j],color=BLUE,label='Selected cone')
        ax.scatter(trajectory/(cm.KB*temp),normal[:,j],s=15,facecolors='none',edgecolors=ORANGE,label='Repeat means')
        ax.set(xlabel='$E_F/(k_BT)$',ylabel='Normalised '+('$R_H$' if j==0 else '$R_s$'),title=f'({chr(97+j)}) {label}')
        ax.legend(loc='best')
    ax=axes[1,0]
    ax.plot(index,trajectory,color=BLUE,label='Central estimate',lw=1.5)
    ax.fill_between(index,efq[0],efq[2],color=BLUE,alpha=.23,label='16–84% resampling interval')
    ax.axhline(0,color='0.6',lw=.7)
    ax.set(xlabel='Measurement index',ylabel='$E_F$ (eV)',title='(c) Fermi level in acquisition order')
    ax.legend()
    ax=axes[1,1]
    ax.plot(index,normal[:,0]-fitted[:,0],'.-',color=BLUE,label='Hall channel',lw=.8)
    ax.plot(index,normal[:,1]-fitted[:,1],'x--',color=ORANGE,label='Sheet channel',lw=.8)
    ax.axhline(0,color='0.6',lw=.7)
    ax.set(xlabel='Measurement index',ylabel='Normalised residual',title='(d) Data minus fitted model')
    ax.legend()
    save_figure(fig,'fig3_l2')
    fig,axes=plt.subplots(1,3,figsize=(10,3.2),layout='constrained')
    scales=np.array([abs(mean[:,0]).max(),mean[:,1].max()])
    for k,color in enumerate([BLUE,ORANGE,GREY]): axes[0].plot(index,reps[:,k,0],'.-',color=color,alpha=.7,label=f'Repeat {k+1}',lw=.7)
    axes[0].axhline(0,color='0.5',lw=.7)
    axes[0].set(xlabel='Measurement index',ylabel='Raw $R_H$ (supplied units)',title='(a) Signed Hall repeats')
    axes[0].ticklabel_format(axis='y',style='sci',scilimits=(0,0))
    axes[0].set_title('(a) Signed Hall repeats',pad=15)
    axes[0].legend(fontsize=8)
    axes[1].plot(gaps[1:],rms[1:],color=BLUE)
    axes[1].axhline(.85*rms[0],color=GREY,ls=':',label='0.85 × cone RMS')
    axes[1].scatter(gaps[selected],rms[selected],color=ORANGE)
    axes[1].set(xlabel='Candidate $E_g/(k_BT)$',ylabel='Pair-space RMS',title='(b) Model selection')
    axes[1].legend(fontsize=8)
    axes[2].hist(boot_gap,bins=np.arange(-.125,8.376,.25),color=BLUE)
    axes[2].set(xlabel='Selected $E_g/(k_BT)$',ylabel='Resampling runs',title='(c) 200 paired resamples')
    save_figure(fig,'fig4_l2_checks')
    result=dict(model='cone' if selected==0 else 'hard_gap',Eg_kT=float(gaps[selected]),
                Eg_uncertainty_kT=float((q[2]-q[0])/2),EF_trajectory_eV=trajectory.tolist())
    return result,summary


def analyse_l3():
    A=np.load(DATA/'L3_A.npy'); scans=np.loadtxt(DATA/'L3_d.csv',delimiter=',')
    d=scans.mean(axis=0); sigma=scans.std(axis=0,ddof=1)
    L=cm.gradient_matrix(); P=np.eye(100)-np.ones((100,100))/100
    singular=np.linalg.svd(A,compute_uv=False)
    eta0=.01*np.linalg.norm(A,2)**2/np.linalg.norm(L,2)**2
    curves=[]; maps=[]; operators=[]
    for factor in [.01,.1,1,10,100]:
        eta=eta0*factor
        operator=P@np.linalg.solve(P@(A.T@A+eta*L.T@L)@P+1e-9*np.eye(100),P@A.T)
        m=operator@d
        curves.append([factor,eta,float(np.linalg.norm(A@m-d)),float(np.linalg.norm(L@m)),float(abs(m).max())])
        maps.append(m);operators.append(operator)
    # The existing G29 regular and blind analyses both used this factor.
    operator=operators[0]; m=maps[0]
    noise_norm=float(np.linalg.norm(sigma)/np.sqrt(3))
    rng=np.random.default_rng(cm.SEED_L3)
    noise=operator@rng.normal(0,sigma,size=(500,128)).T
    maxima=abs(noise).max(axis=0); detection=float(np.percentile(maxima,95))
    centres=np.linspace(-2.7,2.7,10); xx,yy=np.meshgrid(centres,centres[::-1])
    responses=[]; widths=[]
    for row,col in [(5,5),(2,2)]:
        q=np.zeros(100);q[row*10+col]=1;q-=q.mean()
        response=(operator@A@q).reshape(10,10);responses.append(response)
        w=np.maximum(response,0); r2=(xx-centres[col])**2+(yy-centres[::-1][row])**2
        widths.append(float(2.355*np.sqrt((w*r2).sum()/(2*w.sum()))))
    def feature(k,sign):
        row,col=divmod(int(k),10)
        return dict(sign=sign,row=row,column=col,x_probe_pitch=float(centres[col]),
                    y_probe_pitch=float(centres[::-1][row]),amplitude_fraction=float(m[k]))
    features=[feature(m.argmax(),'positive'),feature(m.argmin(),'negative')]
    a=float(abs(m).max()); threshold=.03
    confidence='clear pass' if a+detection<threshold else ('clear fail' if a-detection>threshold else 'borderline')
    assert A.shape==(128,100) and scans.shape==(3,128)
    assert abs(A.sum(axis=1)).max()<1e-11 and abs(m.mean())<1e-12
    summary=dict(eta0=float(eta0),eta=float(eta0*.01),row_sum_max=float(abs(A.sum(axis=1)).max()),
                 mean_map=float(m.mean()),rank=int(np.linalg.matrix_rank(A)),singular_values=singular.tolist(),
                 noise_mean_norm=noise_norm,regularisation=curves,max_abs_map=a,detection_limit=detection,
                 threshold=threshold,envelope=[a-detection,a+detection],resolution_widths=widths,
                 features=features,confidence=confidence,
                 null_constant_norm=float(np.linalg.norm(A@np.ones(100))),
                 resolution_trace=float(np.trace(operator@A)))
    pd.DataFrame(curves,columns=['eta_factor','eta','residual_norm','roughness','max_abs_map']).to_csv(ROOT/'evidence/l3_regularisation.csv',index=False)
    np.savez(ROOT/'evidence/l3_diagnostics.npz',map=m,A=A,scans=scans,sigma=sigma,noise_maxima=maxima,
             responses=responses,regularisation_maps=maps,resolution_matrix=operator@A)
    fig,axes=plt.subplots(1,2,figsize=(10,3.8),layout='constrained')
    limit=abs(m).max()*100
    im=axes[0].imshow(m.reshape(10,10)*100,cmap='RdBu_r',vmin=-limit,vmax=limit,extent=[-3,3,-3,3],origin='upper',interpolation='nearest')
    for f in features:
        axes[0].scatter(f['x_probe_pitch'],f['y_probe_pitch'],s=60,marker='o',edgecolors='black',facecolors='none')
    axes[0].set(xlabel='$x$ / probe pitch',ylabel='$y$ / probe pitch',title='(a) Relative Hall conductivity')
    fig.colorbar(im,ax=axes[0],label='Deviation (%)',shrink=.86)
    axes[1].plot(d, A@m,'o',ms=3,color=BLUE)
    ends=[min(d.min(),(A@m).min()),max(d.max(),(A@m).max())]
    axes[1].plot(ends,ends,'--',color=GREY,lw=1)
    axes[1].set(xlabel='Mean measured signal',ylabel=r'Reconstructed signal $A\hat m$',title='(b) Forward consistency')
    axes[1].ticklabel_format(axis='both',style='sci',scilimits=(0,0))
    save_figure(fig,'fig5_l3')
    fig,axes=plt.subplots(2,2,figsize=(10,6.6),layout='constrained')
    arr=np.array(curves)
    axes[0,0].semilogy(arr[:,3],arr[:,2],'o-',color=BLUE)
    axes[0,0].xaxis.set_major_locator(MaxNLocator(3))
    axes[0,0].axhline(noise_norm,ls='--',color=GREY,label='Expected mean-noise norm')
    for row in arr: axes[0,0].annotate(f'{row[0]:g}',(row[3],row[2]),xytext=(4,4),textcoords='offset points',fontsize=8)
    axes[0,0].set(xlabel=r'Roughness $\|L\hat m\|$',ylabel=r'Residual $\|A\hat m-\bar d\|$',title=r'(a) Regularisation factors $\eta/\eta_0$')
    axes[0,0].legend(fontsize=8)
    axes[0,1].semilogy(np.arange(1,101),singular,'-',color=BLUE)
    axes[0,1].set(xlabel='Singular-value index',ylabel='Singular value',title='(b) Spectrum of $A$')
    im=axes[1,0].imshow(responses[0],cmap='RdBu_r',extent=[-3,3,-3,3],origin='upper',vmin=-abs(responses[0]).max(),vmax=abs(responses[0]).max())
    axes[1,0].set(xlabel='$x$ / probe pitch',ylabel='$y$ / probe pitch',title='(c) Central zero-mean impulse response')
    fig.colorbar(im,ax=axes[1,0],shrink=.8,label='Response amplitude')
    axes[1,1].hist(maxima*100,bins=25,color=BLUE)
    axes[1,1].axvline(detection*100,color=ORANGE,ls='--',label='95th percentile')
    axes[1,1].set(xlabel='Maximum noise-map deviation (%)',ylabel='Noise runs',title='(d) 500 noise-only reconstructions')
    axes[1,1].legend()
    axes[1,1].xaxis.set_major_locator(MaxNLocator(4))
    save_figure(fig,'fig6_l3_checks')
    result=dict(map=m.tolist(),features=features,resolution_probe_pitch=max(widths),
                detection_limit_fraction=detection,pass_=bool(a<=threshold),confidence=confidence)
    result['pass']=result.pop('pass_')
    return result,summary


def main():
    OUT.mkdir(exist_ok=True)
    (ROOT/'evidence').mkdir(exist_ok=True)
    verify_data(DATA)
    results=cm.read_json(DATA/'results_template.json')
    summary={}
    for key,method in [('L1',analyse_l1),('L2',analyse_l2),('L3',analyse_l3)]:
        results[key],summary[key]=method()
        print(key,json.dumps({k:v for k,v in summary[key].items() if k not in ['singular_values','regularisation']}),flush=True)
    try:
        repo=Path(subprocess.check_output(['git','-C',str(ROOT),'rev-parse','--show-toplevel'],text=True,stderr=subprocess.DEVNULL).strip()).resolve()
        if repo != ROOT.resolve(): raise subprocess.CalledProcessError(1,'git repository root')
        results['pipeline_commit']=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True,stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:
        results['pipeline_commit']=(ROOT/'source_commit.txt').read_text().strip() if (ROOT/'source_commit.txt').exists() else 'uncommitted development run'
    save_json(ROOT/'results.json',results)
    save_json(ROOT/'evidence/numerical_summary.json',summary)
    assert len(results['L3']['map'])==100 and len(results['L2']['EF_trajectory_eV'])==summary['L2']['n_measurements']
    verify_data(ROOT/'data/blind_G29')
    archived=cm.read_json(ROOT/'evidence/blind_archive/blind_results.json')
    blind_l1=cm.l1(ROOT/'data/blind_G29')
    blind_l2,_=cm.l2(ROOT/'data/blind_G29',[])
    blind_l3=cm.l3(ROOT/'data/blind_G29',[])
    def compare(current, prior):
        if isinstance(current,dict):
            assert current.keys()==prior.keys()
            for key in current: compare(current[key],prior[key])
        elif isinstance(current,list) and current and isinstance(current[0],dict):
            assert len(current)==len(prior)
            for x,y in zip(current,prior): compare(x,y)
        elif isinstance(current,(str,bool)):
            assert current==prior
        else:
            np.testing.assert_allclose(current,prior,rtol=1e-10,atol=1e-12)
    for section,current in [('L1',blind_l1),('L2',blind_l2),('L3',blind_l3)]:
        compare(current,archived[section])
    save_json(ROOT/'evidence/blind_reproduction_check.json',{'numeric_match':True,'feature_match':True,'decision_match':True,'archived_commit':archived['pipeline_commit']})
    # These are preventive physics checks, not claims that historical errors occurred.
    n=summary['L1']['n_fermi_cm2'];rho=summary['L1']['rho_ohm_sq']
    mu_si=1/(cm.QE*(n*1e4)*rho)
    np.testing.assert_allclose(mu_si*1e4,results['L1']['mobility_corrected_cm2_Vs'])
    _,pairs,_=cm.l2_repeats(DATA)
    hall=pairs.mean(axis=1)[:,0]
    assert (hall<0).any() and (hall>0).any()
    assert np.array_equal(np.sign(cm.normalise(pairs.mean(axis=1))[:,0]),np.sign(hall))
    template=cm.read_json(DATA/'results_template.json')
    assert results.keys()==template.keys()
    for section in ['L1','L2','L3']: assert results[section].keys()==template[section].keys()
    save_json(ROOT/'evidence/physics_checks.json',{
        'status':'preventive validation; no historical failure claimed',
        'mobility_from_SI_converted_to_cm2_Vs':float(mu_si*1e4),
        'mobility_from_cm2_density':results['L1']['mobility_corrected_cm2_Vs'],
        'signed_Hall_preserved':True,'Hall_zero_brackets':summary['L2']['neutrality_brackets'],
        'schema_keys_match':True})
    save_json(ROOT/'evidence/runtime.json',{'python':sys.version.split()[0],
        'numpy':np.__version__,'pandas':pd.__version__,'matplotlib':matplotlib.__version__,
        'platform':platform.platform(),'figure_font':FIGURE_FONT,'pipeline_commit':results['pipeline_commit'],
        'seeds':{'L2':cm.SEED_L2,'L3':cm.SEED_L3}})


if __name__=='__main__':
    class Tee:
        def __init__(self,*streams): self.streams=streams
        def write(self,message):
            for stream in self.streams: stream.write(message)
        def flush(self):
            for stream in self.streams: stream.flush()
    with (ROOT/'run_log.txt').open('w') as logfile:
        terminal=sys.stdout
        sys.stdout=Tee(terminal,logfile)
        try:
            print('Report reproduction UTC '+datetime.now(timezone.utc).isoformat())
            main()
            print('All input, schema, physics and historical blind checks passed.')
        finally:
            sys.stdout=terminal
