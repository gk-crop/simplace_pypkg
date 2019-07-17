"""
Control the simulation framework Simplace.

You need Java >= 8.0 and the Simplace simulation 
framework http://www.simplace.net/

**Example 1** - *Running a project:*

    >>> import simplace
    >>> sp = simplace.initSimplace('/ws/','/runs/simulation/','/out/')
    >>> simplace.setProjectLines(sp, [1,3,8,9,17])
    >>> simplace.openProject(sp, '/sol/Maize.sol.xml', '/proj/NRW.proj.xml')
    >>> simplace.runProject(sp)
    >>> simplace.closeProject(sp)

**Example 2** - *Running a solution with changed simulation parameters:*

    >>> import simplace
    >>> sp = simplace.initSimplace('/ws/','/runs/simulation/','/out/')
    >>> simplace.openProject(sp, '/sol/Maize.sol.xml')
    >>> simid = simplace.createSimulation(sp, {'vLUE':3.2,'vSLA':0.023})
    >>> simplace.runSimulations(sp)
    >>> result = simplace.resultToList(simplace.getResult(sp,'YearOut',simid))
    >>> simplace.closeProject(sp)
    >>> print(result['BiomassModule.Yield'])
    805.45

"""

import jpype
import os


# Initialisation

def initSimplace (installDir, workDir, outputDir,
                  projectsDir = None, dataDir = None, 
                  additionalClasspathList=[], javaParameters=''):   
    """Initialisation of Simplace 
    
    Start the java virtual machine and initialize
    the Simplace framework. You have to call this function first.
    
    Args:
        installDir (str): Where your simplace_core, simplace_modules, simplace_run etc. reside
        workDir (str): Working directory for Simplace solutions, projects
        outputDir (str): Output files will be written there
        projectsDir (Optional[str]): Optional folder for project data
        dataDir (Optional[str]): Optional folder for input data
        additionalClasspathList (Optional[list]): List with addtional classpath
        javaParameters (Optional[str]): Parameters passed to the java virtual 
            machine
        
    Returns:
        SimplaceWrapper : A reference to an instance of SimplaceWrapper 
            java class
    
    """
    
    cpliblist = [os.path.join(directory,filenm) 
                for directory, _, files in os.walk(os.path.join(installDir,"simplace_core","lib")) 
                    for filenm in files 
                        if filenm.lower().endswith('.jar')]
    
    cplist = [
        'simplace_core/build/classes',
        'simplace_core/conf',
        'simplace_modules/build/classes',
        'simplace_run/build/classes',
        'simplace_run/conf',
        'simplace_core/res/files'  
    ]
    
    fullpathcplist = [installDir + s for s in cplist]
    allcplist = fullpathcplist + cpliblist + additionalClasspathList
    cpstring = os.pathsep.join(allcplist)
    cp = '-Djava.class.path='+cpstring
    if hasattr(jpype,'__version_info__') and (jpype.__version_info__[0]>0 or jpype.__version_info__[1]>6) :
        jpype.startJVM(jpype.getDefaultJVMPath(), cp, javaParameters, ignoreUnrecognized=True, convertStrings=False)
    else :
        jpype.startJVM(jpype.getDefaultJVMPath(), cp, javaParameters)
    Wrapper = jpype.JClass('net.simplace.sim.wrapper.SimplaceWrapper')
    simplaceInstance = Wrapper(workDir, outputDir, projectsDir, dataDir)
    return simplaceInstance


# Open and close Project

def openProject(simplaceInstance,solution, project=None):
    """Create a project from the solution and optional project file."""
    simplaceInstance.prepareSession(project, solution)
        
def closeProject(simplaceInstance):
    """Close the project."""
    simplaceInstance.shutDown()        


# Running and configuring projects

def setProjectLines(simplaceInstance, lines):
    """Set the line numbers of the project data file used for simulations."""
    if type(lines) is list :
        lines = ','.join([str(i) for i in lines])
    simplaceInstance.setProjectLines(lines)   

def runProject(simplaceInstance):
    """Run the project."""
    simplaceInstance.run()


# Creating, configuring and running simulations

def createSimulation(simplaceInstance, parameters = None, queue=True):
    """Create a single simulation and set initial parameters."""
    par = _parameterListToArray(parameters)
    simplaceInstance.createSimulation(par)
    return str(getSimulationIDs(simplaceInstance)[-1])

def getSimulationIDs(simplaceInstance):
    """Get the ids of ready to run simulations."""
    return [str(s) for s in simplaceInstance.getSimulationIDs()]

def setSimulationValues(simplaceInstance, parameters):
    """Set values of actual simulation that runs stepwise."""
    simplaceInstance.setSimulationValues(_parameterListToArray(parameters))
    
def setAllSimulationValues(simplaceInstance, parameterlist):
    """Set values of all simulations in queue."""
    simplaceInstance.setAllSimulationValues(_parameterListsToArray(parameterlist))

def runSimulations(simplaceInstance, selectsimulation = False):
    """Run created simulations."""
    simplaceInstance.runSimulations(selectsimulation)

def stepSimulation(simplaceInstance, count=1, parameters=None, varFilter=None, 
                   simulationnumber=0):
    """Run specific simulation stepwise (default first simulation in queue)."""
    par = _parameterListToArray(parameters)
    return simplaceInstance.stepSpecific(simulationnumber, par, varFilter,count)

def stepAllSimulations(simplaceInstance, count=1, parameterlist=None, varFilter=None):
    """Run all simulations in queue stepwise."""
    par = _parameterListsToArray(parameterlist)
    return simplaceInstance.stepAll(par,varFilter,count)


# Fetch results and convert it to python objects.
    
def getResult(simplaceInstance, output, simulation):
    """Get a specific output of a finished simulation."""
    return simplaceInstance.getResult(output, simulation)

def resultToList(result, expand = True, start=None, end=None):
    """Convert the output to a python dictionary"""
    if(start is not None and end is not None and start <= end and start >= 0):
        obj =  result.getDataObjects(start, end)
    else :
        obj =  result.getDataObjects()
    names = [str(s) for s in result.getHeaderStrings()]
    types = [str(s) for s in result.getTypeStrings()]
    val = [_objectArrayToData(*z, expand = expand) for z in zip(obj, types)]
    return dict(zip(names, val))

def varmapToList(result, expand = True):
    """Convert the values of the last simulation step to a python dictionary."""
    names = [str(s) for s in result.getHeaderStrings()]
    obj =  result.getDataObjects()
    types = [str(s) for s in result.getTypeStrings()]
    val = [_objectToData(*z, expand = expand) for z in zip(obj,types)]
    return dict(zip(names, val))

def getUnitsOfResult(result):
    """Get the list of units of the output variables."""
    names = [str(s) for s in result.getHeaderStrings()]
    units = [str(s) for s in result.getHeaderUnits()]
    return dict(zip(names,units))


# Configuration

def setSimplaceDirectories(simplaceInstance, 
                           workDir = None, outputDir = None, 
                           projectsDir = None, dataDir = None):
    """Set work-, output-, projects- and data-directory."""   
    simplaceInstance.setDirectories(workDir, outputDir, projectsDir, dataDir)  

def getSimplaceDirectories(simplaceInstance):
    """Get work-, output-, projects- and data-directory.""" 
    names = ["_WORKDIR_", "_OUTPUTDIR_", "_PROJECTSDIR_", "_DATADIR_"]
    return dict(zip(names, [str(s) for s in simplaceInstance.getDirectories()]))  

def setSlotCount(count):
    """Set the maximum numbers of processors used  when running projects."""   
    jpype.JClass('net.simplace.sim.FWSimEngine').setSlotCount(count)  
        
def setLogLevel(level):
    """Set the log's verbosity. Ranges from least verbose 
        'ERROR','WARN','INFO','DEBUG' to most verbose 'TRACE'.
    """
    LOG = jpype.JClass('net.simplace.core.logging.Logger')
    LOGL = jpype.JClass('net.simplace.core.logging.Logger$LOGLEVEL')
    LOG.setLogLevel(LOGL.valueOf(level))
    
def setCheckLevel(simplaceInstance, level):
    """Set the checklevel of the solution."""
    simplaceInstance.setCheckLevel(level)   


# Helper Functions

def _objectArrayToData(obj, simplaceType, expand = True):
    au = 'org.apache.commons.lang.ArrayUtils'
    if (simplaceType in ['DOUBLE','INT','BOOLEAN']):
        return list(jpype.JClass(au).toPrimitive(obj))
    elif (simplaceType in ['DATE']):
        return [str(s)[:10] for s in obj]
    elif (simplaceType in ['CHAR']):
        return [str(s) for s in obj]
    elif expand and simplaceType in ['DOUBLEARRAY','INTARRAY']:
        return [list(jpype.JClass(au).toPrimitive(row)) for row in obj]
    elif expand and simplaceType in ['CHARARRAY']:
        return [[str(s) for s in row] for row in obj]
    else:
        return list(obj)
            
def _objectToData(obj, simplaceType, expand = True):
    au = 'org.apache.commons.lang.ArrayUtils'
    if (simplaceType in ['DOUBLE']):
        return obj.doubleValue()
    elif (simplaceType in ['INT']):
        return obj.intValue()
    elif expand and simplaceType in ['DOUBLEARRAY','INTARRAY']:
        return list(jpype.JClass(au).toPrimitive(obj))
    elif simplaceType in ['DATE']:
        return str(obj)[:10]
    elif simplaceType in ['CHAR']:
        return str(obj)
    else:
        return obj            
    
def _parameterListToArray(parameter):
    if parameter is None:
        return None
    else:
        return jpype.JArray(jpype.java.lang.Object, 2)(
          [[k, _getScalarOrList(v)] for k, v in parameter.items()])

def _parameterListsToArray(parameterlist):
    if parameterlist is None:
        return None
    else:
        return jpype.JArray(jpype.java.lang.Object, 3)(
          [[[k, _getScalarOrList(v)] for k, v in par.items()] 
           for par in parameterlist])

    
def _getScalarOrList(obj):
    if type(obj) is list:
        if all(type(a) is int for a in obj) :
            return jpype.JArray(jpype.JInt, 1)(obj)
        else:
            return jpype.JArray(jpype.JDouble, 1)(obj)
    else:
        if type(obj) is int :
            return jpype.java.lang.Integer(obj)
        else:
            return obj