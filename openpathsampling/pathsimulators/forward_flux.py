import logging
import numpy as np
import openpathsampling as paths

logger = logging.getLogger(__name__)
from .shoot_snapshots import ShootFromSnapshotsSimulation
from .path_simulator import PathSimulator, MCStep

class ForwardFluxSimulation(PathSimulator):
    """ Forward Flux simulations.
    Parameters
    ----------
    storage : :class:`.Storage`
        the file to store simulations in
    engine : :class:`.DynamicsEngine`
        the dynamics engine to use to run the simulation
    states : list of :class:`.Volume`
        the volumes representing the stable states, first state A then state B
    #randomizer : :class:`.SnapshotModifier`
    #    the method used to modify the input snapshot before each shot
    initial_snapshots : list of :class:`.Snapshot`
        initial snapshots to use
    rc : :class:`.CollectiveVariable`
        reaction coordinate
    """
    def __init__(self, storage=None, engine=None, states=None,
                 interfacesA=None, randomizer=None, initial_sample_set=None,
                 ensemble=None, rc=None):
                
        self.storage = storage
        self.engine = engine
        paths.EngineMover.default_engine = engine
        self.states = states
        self.A = states[0]
        self.B = states[1]
        self.interfacesA = interfacesA
        self.randomizer = randomizer
        self.initial_sample_set = initial_sample_set
        self.ensemble=ensemble
        self.rc = rc
        
        # self.current_ensemble = paths.SequentialEnsemble([
        #     paths.AllInXEnsemble(A) & paths.LengthEnsemble(1),
        #     paths.AllInXEnsemble(interfacesA[0]),
        #     paths.AllOutXEnsemble(interfacesA[0]) & paths.LengthEnsemble(1)
        # ])
        
        # self.forward_ensemble = paths.SequentialEnsemble([
        #     paths.AllInXEnsemble(A) & paths.LengthEnsemble(1),
        #     paths.AllInXEnsemble(interfacesA[1]) & paths.LengthEnsemble(1),
        # ])

        super(ForwardFluxSimulation, self).__init__(storage)
            
        # self.forward_mover = paths.ForwardExtendMover(
        #     ensemble=self.current_ensemble,
        #     target_ensemble=self.forward_ensemble
        # )
            
        # self.mover = self.forward_mover
    
       
    def to_dict(self):
        ret_dict = {
            'engine' : self.engine,
            'states' : self.states,
            'interfacesA' : self.interfacesA,
            'randomizer' : self.randomizer,
            'initial_sample_set' : self.initial_sample_set,
            'ensemble' : self.ensemble
        }
        return ret_dict

    @classmethod
    def from_dict(cls, dct):
        ffs = cls.__new__(cls)

        # replace automatically created attributes with stored ones
        ffs.engine = dct['engine']
        ffs.states = dct['states']
        ffs.interfacesA = dct['interfacesA']
        ffs.randomizer = dct['randomizer']
        ffs.initial_sample_set = dct['initial_sample_set']
        ffs.ensemble = dct['ensemble']
        return ffs
    
    def run(self, n_per_interface):
        """
        Runs the actual FFS Simulation.

        Parameters
        ----------
        n_per_interface : int
            number of trial shoots per interface

        Returns
        -------
        None.

        """
        self.output_stream.write("\n")
        
        self.step = 0
        
        ensembles = [self.ensemble]
        
        for num_if in range(len(self.interfacesA)+1):
        #for num_if in range(2):
            
            if num_if == len(self.interfacesA):
                ensembles.append(paths.SequentialEnsemble([
                    paths.AllInXEnsemble(self.A) & paths.LengthEnsemble(1),
                    paths.AllOutXEnsemble(self.B | self.A),
                    paths.AllInXEnsemble(self.B) &
                    paths.LengthEnsemble(1),
                    ]))
            else:
                ensembles.append(paths.SequentialEnsemble([
                    paths.AllInXEnsemble(self.A) & paths.LengthEnsemble(1),
                    paths.AllInXEnsemble(self.interfacesA[num_if]) &
                    paths.AllOutXEnsemble(self.A),
                    paths.AllOutXEnsemble(self.interfacesA[num_if]) &
                    paths.LengthEnsemble(1),
                ]))
            
        
            forward_mover = paths.ForwardExtendMover(
                ensemble=ensembles[-2],
                target_ensemble=ensembles[-1],
                engine = self.engine
            )
            
            mover = forward_mover
            #mover = paths.PathSimulatorMover(mover=forward_mover,
                                             # pathsimulator=self)
            
            for n_shoot in range(n_per_interface):
                
                next_sample_set = paths.SampleSet([])
                
                paths.tools.refresh_output(
                    "Working on interface %d / %d; shoot %d / %d\n" % (
                        num_if+1, len(self.interfacesA)+1,
                        n_shoot+1, n_per_interface
                    ),
                    output_stream=self.output_stream,
                    refresh=self.allow_refresh
                )
                
                #current_ensemble = self.FFSEnsemble
                
                
                
                # sample_set = paths.SampleSet([self.initial_sample_set[1],
                #                               self.initial_sample_set[2]])
                
                # sample_set.sanity_check()
                
                new_pmc = mover.move(self.initial_sample_set)
                samples = new_pmc.results
                # .results returns a list of samples that are accepted in this
                # move
                #new_sample_set.append[self.initial_sample_set.apply_samples(samples)]
                new_sample_set = self.initial_sample_set.apply_samples(samples)
                
                mcstep = MCStep(
                    simulation=self,
                    mccycle=self.step,
                    previous=self.initial_sample_set,
                    active=new_sample_set,
                    change=new_pmc
                )
                
                if self.storage is not None:
                    self.storage.steps.save(mcstep)
                    if self.step % self.save_frequency == 0:
                        self.sync_storage()
                
                next_sample_set.extend(new_sample_set)
                self.step += 1
                
            #self.ensemble = forward_ensemble
            self.initial_sample_set = next_sample_set
            
            
            
        self.output_stream.write("\nDone! Completed %d Monte Carlo cycles."
                                 % self.step)
        return None
            
    
    #     #------------------------------
    #     # FROM REACTIVE FLUX SIMULATION
    #     #------------------------------
        
    #     # # get min/max reaction coordinate of initial snapshots
    #     # self.rc = rc
    #     # rc_array = np.array(self.rc(initial_snapshots))
    #     # rc_min = np.nextafter(rc_array.min(), -np.inf)
    #     # rc_max = np.nextafter(rc_array.max(), np.inf)

    #     # define reaction coordinate region of initial snapshots
    #     # = starting_volume
    #     self.dividing_surface = paths.CVDefinedVolume(self.rc, rc_min, rc_max)

    #     # define volume between state A and the dividing surface (including A)
    #     self.volume_towards_A = paths.CVDefinedVolume(self.rc, -np.inf, rc_max)

    #     # shoot backward until we hit A but never cross the dividing surface
    #     backward_ensemble = paths.SequentialEnsemble([
    #         paths.AllInXEnsemble(state_A) & paths.LengthEnsemble(1),
    #         paths.AllInXEnsemble(self.volume_towards_A - state_A)
    #     ])

    #     # shoot forward until we hit state B without hitting A first
    #     # caution: since the mover will consist of backward and forward
    #     #          shoot in sequence, the starting ensemble for the forward
    #     #          shoot is the output of the backward shoot, i.e. a
    #     #          trajectory that runs from A to the dividing surface and
    #     #          not just a point there.
    #     forward_ensemble = paths.SequentialEnsemble([
    #         paths.AllInXEnsemble(state_A) & paths.LengthEnsemble(1),
    #         paths.AllOutXEnsemble(state_A | state_B),
    #         paths.AllInXEnsemble(state_B) & paths.LengthEnsemble(1),
    #     ])

    #     super(ReactiveFluxSimulation, self).__init__(
    #         storage=storage,
    #         engine=engine,
    #         starting_volume=self.dividing_surface,
    #         forward_ensemble=forward_ensemble,
    #         backward_ensemble=backward_ensemble,
    #         randomizer=randomizer,
    #         initial_snapshots=initial_snapshots
    #     )

    #     # create backward mover (starting from single point)
    #     self.backward_mover = paths.BackwardExtendMover(
    #         ensemble=self.starting_ensemble,
    #         target_ensemble=self.backward_ensemble
    #     )

    #     # create forward mover (starting from the backward ensemble)
    #     self.forward_mover = paths.ForwardExtendMover(
    #         ensemble=self.backward_ensemble,
    #         target_ensemble=self.forward_ensemble
    #     )

    #     # create mover combining forward and backward shooting,
    #     # abort if backward mover fails
    #     self.mover = paths.NonCanonicalConditionalSequentialMover([
    #         self.backward_mover,
    #         self.forward_mover
    #     ])

    # def to_dict(self):
    #     ret_dict = {
    #         'states' : self.states,
    #         'dividing_surface' : self.dividing_surface,
    #         'volume_towards_A' : self.volume_towards_A,
    #         'rc' : self.rc
    #     }
    #     return ret_dict

    # @classmethod
    # def from_dict(cls, dct):
    #     rf = cls.__new__(cls)

    #     # replace automatically created attributes with stored ones
    #     rf.states = dct['states']
    #     rf.dividing_surface = dct['dividing_surface']
    #     rf.volume_towards_A = dct['volume_towards_A']
    #     rf.rc = dct['rc']
    #     return rf