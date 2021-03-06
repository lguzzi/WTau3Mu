import PhysicsTools.HeppyCore.framework.config as cfg
import os
import glob

#####COMPONENT CREATOR

from CMGTools.RootTools.samples.ComponentCreator import ComponentCreator
kreator = ComponentCreator()

## Pythia MC
files_2017_300k = glob.glob('/gwteras/cms/store/user/lguzzi/WToTauNu_Tau3Mu_Pythia_RunIIFall17/crab_miniaod/200502_104949/0000/wtotaunu_tau3mu_phytia_RunIIAutumn17MiniAOD_*.root')

# first private production (BR bug)
#files_2017_300k = glob.glob('/gwteras/cms/store/user/lguzzi/WToTauNu_Tau3Mu_Pythia/CRAB3_MC_generation_300k_miniaod_smallfiles/190313_143423/*/*.root')

## correct private production
WToTauTo3Mu_Pythia = cfg.MCComponent(
    dataset       = 'WToTauTo3Mu',
    name          = 'WToTauTo3Mu',
    files         = files_2017_300k ,
    xSection      = 21490.9, # this uses the correct tau BR from the PDG # 20508.9 * 1.e-7, # W to lep nu / 3.[pb] x BR
    nGenEvents    = 390032,
    effCorrFactor = 1,
)
## central production 
WToTauTo3Mu_MadGraph = kreator.makeMCComponent(
    name        = 'WToTauTo3Mu' ,
    dataset     = '/W_ToTau_ToMuMuMu_TuneCP5_13TeV-pythia8-madgraph/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM',
    user        = 'CMS'         ,
    pattern     = '.*root'      ,
    useAAA      = True          ,
)

WToTauTo3Mu_Pythia_ULcentral = kreator.makeMCComponent(
    name        = 'WToTauTo3Mu' ,
    dataset     = '/W_ToTau_ToMuMuMu_TuneCP5_13TeV-pythia8/RunIISummer19UL17MiniAOD-106X_mc2017_realistic_v6-v2/MINIAODSIM',
    user        = 'CMS'         , 
    pattern     = '.*root'      ,
    useAAA      = True          ,
)
