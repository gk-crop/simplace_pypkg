"""
Control the simulation framework Simplace - Object oriented interface.

It wraps the functions from the simplace package to a class.

You need Java >= 8.0 and the Simplace simulation 
framework http://www.simplace.net

**Example 1** - *Running a project:*

    >>> import simplace
    >>> sim = simplace.SimplaceInstance('/ws/','/runs/simulation/','/out/')
    >>> sim.setProjectLines([1,3,8,9,17])
    >>> sim.openProject('/sol/Maize.sol.xml', '/proj/NRW.proj.xml')
    >>> sim.runProject()
    >>> sim.closeProject()

**Example 2** - *Running a solution with changed simulation parameters:*

    >>> import simplace
    >>> sim = simplace.SimplaceInstance('/ws/','/runs/simulation/','/out/')
    >>> sim.openProject('/sol/Maize.sol.xml')
    >>> simid = sim.createSimulation({'vLUE':3.2,'vSLA':0.023})
    >>> sim.runSimulations()
    >>> result = sim.getResult('YearlyOutput',simid)).toList()
    >>> sim.closeProject()
    >>> print(result['BiomassModule.Yield'])
    805.45

"""

import simplace

class SimplaceInstance:
    """Class to access and control the simulation Framework Simplace"""
    
    def __init__(self, installDir, workDir, outputDir, 
                 additionalClasspathList =[], javaParameters = ''):
        self._sh = simplace.initSimplace(installDir, workDir, outputDir, 
                                  additionalClasspathList, javaParameters)
        
    def openProject(self, solution, project = None):
        """Create a project from the solution and optional project file."""
        simplace.openProject(self._sh, solution, project)
        
    def closeProject(self):
        """Close the project."""
        simplace.closeProject(self._sh)
        
    def runProject(self):
        """Run the project."""
        simplace.runProject(self._sh)
        
    def setProjectLines(self, lines):
        """Set the line numbers of the project data file used for simulations."""
        simplace.setProjectLines(self._sh, lines)
        
    
    
    def createSimulation(self, parameters = None, queue = True):
        """Create a single simulation and set initial parameters."""
        return simplace.createSimulation(self._sh, parameters, queue)
        
    def getSimulationIDs(self):
        """Get the ids of ready to run simulations."""
        return simplace.getSimulationIDs(self._sh)
        
    def setSimulationValues(self, parameters):
        """Set values of actual simulation that runs stepwise."""
        simplace.setSimulationValues(self._sh, parameters)
    
    def runSimulations(self, selectsimulation = False):
        """Run created simulations."""
        simplace.runSimulations(self._sh, selectsimulation)
        
    def stepSimulation(self, count = 1, parameters = None, varFilter = None):
        """Run last created simulation stepwise and return variable map."""
        varmap = simplace.stepSimulation(self._sh, count, parameters, varFilter)
        return SimplaceVarmap(varmap)
        
    def getResult(self, output, simulation):
        """Get a specific output of a finished simulation."""
        result = simplace.getResult(self._sh, output, simulation)
        return SimplaceResult(result)    
    
    
    def setLogLevel(self, level):
        """Set the log's verbosity. Ranges from least verbose 
            'ERROR','WARN','INFO','DEBUG' to most verbose 'TRACE'.
        """
        simplace.setLogLevel(level)
        
    def setCheckLevel(self, level):
        """Set the checklevel of the solution."""
        simplace.setCheckLevel(self._sh, level)
        
    def setSlotCount(self, count):
        """Set the maximum numbers of processors used  when running projects."""   
        simplace.setSlotCount(count)
        
            
    
class SimplaceResult():
    """Result of a Simplace simulation. Returned by getResult() method."""
    
    def __init__(self, result):
        self._rs = result 
               
    def toList(self, expand = True, start = None, end = None):
        """ Return the result as python dictionary."""      
        return simplace.resultToList(self._rs, expand, start, end)  
    def getUnits(self):
        """Get units of the result values."""
        return simplace.getUnitsOfResult(self._rs)    
    


class SimplaceVarmap():
    """Actual Varmap from a simplace step run. Returned by step() method."""    

    def __init__(self, varmap): 
        self._rs = varmap 
        
    def toList(self, expand = True):
        """ Return the varmap as python dictionary."""   
        return simplace.varmapToList(self._rs, expand)    
        
    def getUnits(self):
        """Get units of the varmap values."""
        return simplace.getUnitsOfResult(self._rs)    
