from itertools import product, combinations

from PhysicsTools.Heppy.analyzers.core.Analyzer   import Analyzer
from PhysicsTools.Heppy.analyzers.core.AutoHandle import AutoHandle
from PhysicsTools.Heppy.physicsobjects.Muon       import Muon
from PhysicsTools.Heppy.physicsobjects.Electron   import Electron
from PhysicsTools.Heppy.physicsobjects.Tau        import Tau
from PhysicsTools.HeppyCore.utils.deltar          import deltaR, deltaR2

from CMGTools.WTau3Mu.physicsobjects.Tau3MuMET    import Tau3MuMET

class Tau3MuAnalyzer(Analyzer):
    '''
    '''

    def declareHandles(self):
        super(Tau3MuAnalyzer, self).declareHandles()

        self.handles['taus'] = AutoHandle(
            'slimmedTaus',
            'std::vector<pat::Tau>'
        )

        self.handles['electrons'] = AutoHandle(
            'slimmedElectrons',
            'std::vector<pat::Electron>'
        )

        self.handles['muons'] = AutoHandle(
            'slimmedMuons',
            'std::vector<pat::Muon>'
        )

        self.mchandles['genParticles'] = AutoHandle(
            'prunedGenParticles',
            'std::vector<reco::GenParticle>'
        )

        self.handles['puppimet'] = AutoHandle(
            'slimmedMETsPuppi',
            'std::vector<pat::MET>'
        )

        self.handles['pfmet'] = AutoHandle(
            'slimmedMETs',
            'std::vector<pat::MET>'
        )
        

    def beginLoop(self, setup):
        super(Tau3MuAnalyzer, self).beginLoop(setup)
        self.counters.addCounter('Tau3Mu')
        count = self.counters.counter('Tau3Mu')
        count.register('all events')
        count.register('> 0 vertex')
        count.register('> 0 tri-muon')
#         count.register('fourth muon veto')
#         count.register('electron veto')
#         count.register('trig matched')
        count.register('m < 10 GeV')

    def buildMuons(self, muons, event):
        '''
        '''
        muons = map(Muon, muons)
        for mu in muons:
            mu.associatedVertex = event.vertices[0]
        muons = [mu for mu in muons if 
                 (mu.isSoftMuon(mu.associatedVertex) or mu.isLooseMuon()) and
                 mu.pt()>1. and
                 abs(mu.eta())<2.1]            
        return muons

    def buildElectrons(self, electrons, event):
        '''
        Used for veto
        '''
        map(Electron, electrons)
        for ele in electrons:
            ele.associatedVertex = event.vertices[0]
        electrons = [ele for ele in electrons if
                     ele.pt()>10 and
                     abs(ele.eta())<2.5 and
                     self.testVertex(ele) and
                     ele.mvaIDRun2('POG_SPRING16_25ns_v1_Veto') and
                     ele.passConversionVeto() and
                     ele.physObj.gsfTrack().hitPattern().numberOfHits(ROOT.reco.HitPattern.MISSING_INNER_HITS) <= 1 and
                     ele.relIsoR(R=0.3, dBetaFactor=0.5, allCharged=0) < 0.3]
        return electrons

    def buildTaus(self, taus, event):
        '''
        '''
        map(Tau, taus)
        taus = [tau for tau in taus if 
                tau.tauID('decayModeFinding') > 0.5 and
                tau.tauID('byLooseIsolationMVArun2v1DBoldDMwLT') > 0.5 and
                tau.pt()>18. and
                abs(tau.eta())<2.3 and
                self.testTauVertex(tau)]
        return map(Tau, taus)
    
    def process(self, event):
        self.readCollections(event.input)

        if len(event.vertices):
            self.counters.counter('Tau3Mu').inc('> 0 vertex')
        else:
            return False

        event.muons     = self.buildMuons    (self.handles['muons'    ].product(), event)
        event.electrons = self.buildElectrons(self.handles['electrons'].product(), event)
        event.taus      = self.buildTaus     (self.handles['taus'     ].product(), event)
        event.pfmet     = self.handles['pfmet'   ].product()[0]
        event.puppimet  = self.handles['puppimet'].product()[0]

        # to be implemented
        # event.vetoelectrons = [ele for ele in event.electrons if self.isVetoElectron(ele)]
        # event.vetotaus      = [tau for tau in event.taus      if self.isVetoTau(tau)     ]
        
        event.tau3mus = [Tau3MuMET(triplet, event.pfmet) for triplet in combinations(event.muons, 3)]

        good = self.selectionSequence(event)
        
        return good

    def selectionSequence(self, event):

        self.counters.counter('Tau3Mu').inc('all events')

        if len(event.muons) < 3:
            return False

        self.counters.counter('Tau3Mu').inc('> 0 tri-muon')

        # testing di-lepton itself
        seltau3mu = event.tau3mus

        # mass cut
        seltau3mu = [triplet for triplet in seltau3mu if triplet.massMuons() < 10.]
        
        if len(seltau3mu) == 0:
            return False
        self.counters.counter('Tau3Mu').inc('m < 10 GeV')

        event.seltau3mu = seltau3mu

        event.tau3mu = self.bestTriplet(seltau3mu)

        return True


    def bestTriplet(self, triplets):
        '''
        The best triplet is the one with the correct charge and highest mT(3mu, MET). 
        If there are more than one triplets with the wrong charge, take the one with the highest  mT(3mu, MET).
        '''
        triplets.sort(key=lambda tt : (abs(tt.mu1().charge() + tt.mu2().charge() + tt.mu3().charge())==1 * tt.mttau()) - (abs(tt.mu1().charge() + tt.mu2().charge() + tt.mu3().charge())!=1 / max(tt.mttau(), 1.e-12)), reverse=True )
        return triplets[0]
    
    def testVertex(self, lepton):
        '''Tests vertex constraints, for mu'''
        try:
            return abs(lepton.dxy()) < 0.045 and abs(lepton.dz()) < 0.2
        except:
            import pdb ; pdb.set_trace()
        
    def testTauVertex(self, tau):
        '''Tests vertex constraints, for tau'''
        # Just checks if the primary vertex the tau was reconstructed with
        # corresponds to the one used in the analysis
        # isPV = abs(tau.vertex().z() - tau.associatedVertex.z()) < 0.2
        isPV = abs(tau.leadChargedHadrCand().dz()) < 0.2
        return isPV

    