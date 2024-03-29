"""
Control the simulation framework Simplace.

You need Java >= 11.0 and the Simplace simulation
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
import numpy

# Initialisation

def initSimplace (installDir = None, workDir = None, outputDir = None,
                  projectsDir = None, dataDir = None,
                  additionalClasspathList=[], javaParameters=None):
    """Initialisation of Simplace

    Start the java virtual machine and initialize
    the Simplace framework. You have to call this function first.

    Args:
        installDir (str): Where your simplace_core, simplace_modules,
            simplace_run etc. reside
        workDir (str): Working directory for Simplace solutions, projects
        outputDir (str): Output files will be written there
        projectsDir (str): Optional folder for project data
        dataDir (str): Optional folder for input data
        additionalClasspathList (list): List with addtional classpaths
        javaParameters (str[]): Parameter list passed to the java virtual
            machine

    Returns:
        SimplaceWrapper : A reference to an instance of SimplaceWrapper
            java class

    """

    if (installDir == None):
        installDir = findFirstSimplaceInstallation()

    if(workDir == None):
        workDir = os.path.join(installDir,'simplace_run/simulation/')

    if(outputDir == None):
        outputDir = os.path.join(installDir,'simplace_run/output/')

    cpliblist = [os.path.join(directory,filenm)
                for directory, _, files in os.walk(os.path.join(installDir,"simplace_core","lib"))
                    for filenm in files
                        if filenm.lower().endswith('.jar')]
    cpliblist = cpliblist + [os.path.join(directory,filenm)
                for directory, _, files in os.walk(os.path.join(installDir,"lib"))
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

    if javaParameters==None:
        javaParameters=[]
    if isinstance(javaParameters,str):
        javaParameters=[javaParameters]

    jpype.startJVM(*javaParameters, jvmpath=jpype.getDefaultJVMPath(), classpath=allcplist, ignoreUnrecognized=True, convertStrings=False)
    Wrapper = jpype.JClass('net.simplace.sim.wrapper.SimplaceWrapper')
    simplaceInstance = Wrapper(workDir, outputDir, projectsDir, dataDir)
    return simplaceInstance

def shutDown(simplaceInstance):
    """
    Stops the java virtual machine.

    Parameters:
        simplaceInstance: handle to the SimplaceWrapper object returned by
            initSimplace
    """
    simplaceInstance.shutDown()
    jpype.java.lang.System.exit(0)


def initSimplaceDefault(setting="run"):
    """
    Initialises Simplace with work- and outputdir for different settings

    Args:
        setting (str): one of 'run', 'modules', 'lapclient' or 'wininstall'

    Returns:
        SimplaceWrapper : A reference to an instance of SimplaceWrapper
            java class

    """
    d = findFirstSimplaceInstallation()
    print(d)
    if setting == "modules":
        wd = os.path.join(d,"simplace_modules/test/")
        od = os.path.join(d,"simplace_modules/output/")
    elif setting == "lapclient":
        wd = os.path.join(d,"lapclient/data/")
        od = os.path.join(d,"lapclient/output/")
    elif setting == "wininstall":
        hd = os.path.expanduser('~')
        wd = os.path.join(hd,"SIMPLACE_WORK/")
        od = os.path.join(hd,"SIMPLACE_WORK/output/")
    else:
        wd = os.path.join(d,"simplace_run/simulation/")
        od = os.path.join(d,"simplace_run/output/")
    print(wd)
    print(od)
    return initSimplace(d, wd, od)



# Open and close Project

def openProject(simplaceInstance,solution, project=None, parameters=None):
    """
    Initialises a project from the solution and optional project file.

    Args:
        simplaceInstance : handle to the SimplaceWrapper object returned by
            initSimplace
        solution (str): path (absolute or relative to workDir) to solution file
        project (str): path (abs. or rel. to workDir) to project file (optional)
        parameters (dict): key-value pairs where the key has to match the
            Simplace SimVariable name (optional)

    """
    dirs = getSimplaceDirectories(simplaceInstance)

    if not os.path.exists(solution):
        newsolution = os.path.join(dirs['_WORKDIR_'], solution.lstrip("\\/"))
        if os.path.exists(newsolution):
            solution = newsolution
    if (project != None and not os.path.exists(project)):
        newproject = os.path.join(dirs['_WORKDIR_'], project.lstrip("\\/"))
        if os.path.exists(newproject):
            project = newproject

    par = _parameterListToArray(parameters)
    simplaceInstance.prepareSession(project, solution, par)

def closeProject(simplaceInstance):
    """
    Close the project.

    Parameters:
        simplaceInstance: handle to the SimplaceWrapper object returned by
            initSimplace
    """
    simplaceInstance.shutDown()


# Running and configuring projects

def setProjectLines(simplaceInstance, lines):
    """
    Set the line numbers of the project data file used for simulations.

    Args:
        simplaceInstance: handle to the SimplaceWrapper object returned by
            initSimplace
        lines (str): a string with line specifications, e.g. "3-10,15,30-33"
            or a list of linenumbers [1,2,9,11]
    """
    if type(lines) is list :
        lines = ','.join([str(i) for i in lines])
    simplaceInstance.setProjectLines(lines)

def runProject(simplaceInstance):
    """
    Run the project.

    Args:
        simplaceInstance: handle to the SimplaceWrapper object returned by
            initSimplace
    """
    simplaceInstance.run()


# Creating, configuring and running simulations

def createSimulation(simplaceInstance, parameters = None, queue=True):
    """
    Create a single simulation and set initial parameters.

    Args:
        simplaceInstance :  handle to the SimplaceWrapper object returned by
            initSimplace
        parameters (dict): key-value pairs where the key has to match the
            Simplace SimVariable name (optional)
        queue (bool): if true add the simulation to the queue of simulations,
            else empty the queue before adding the simulation

    Returns:
        str : id of the created simulation

    """
    par = _parameterListToArray(parameters)
    simplaceInstance.createSimulation(par)
    return str(getSimulationIDs(simplaceInstance)[-1])

def getSimulationIDs(simplaceInstance):
    """
    Get the ids of ready to run simulations.

    Args:
        simplaceInstance : handle to the SimplaceWrapper object returned by
            initSimplace

    Returns:
        list : list of simulation ids

    """
    return [str(s) for s in simplaceInstance.getSimulationIDs()]

def setSimulationValues(simplaceInstance, parameters):
    """
    Set values of actual simulation that runs stepwise.

    Args:
        simplaceInstance : handle to the SimplaceWrapper object returned by
            initSimplace
        parameters (dict) : key-value pairs where the key has to match the
            Simplace SimVariable name
    """
    simplaceInstance.setSimulationValues(_parameterListToArray(parameters))

def setAllSimulationValues(simplaceInstance, parameterlist):
    """
    Set values of all simulations in queue.

    Args:
        simplaceInstance: handle to the SimplaceWrapper object returned by
            initSimplace
        parameterlist (list): a list of dictinaries with key-value pairs where
            the key has to match the Simplace SimVariable name
    """
    simplaceInstance.setAllSimulationValues(_parameterListsToArray(parameterlist))

def runSimulations(simplaceInstance, selectsimulation = False):
    """
    Run created simulations.

    Args:
        simplaceInstance: handle to the SimplaceWrapper object returned by
            initSimplace
        selectsimulation (bool): if true, it keeps a selected simulation
            (not yet usable)
    """
    simplaceInstance.runSimulations(selectsimulation)

def stepSimulation(simplaceInstance, count=1, parameters=None, varFilter=None,
                   simulationnumber=0):
    """
    Run specific simulation stepwise (default first simulation in queue).

    Arguments:
        simplaceInstance: handle to the SimplaceWrapper object returned by
            initSimplace
        count (int): number of steps to perform
        parameters (dict): key-value pairs where the key has to match the
            Simplace SimVariable name
        varFilter (list): list of variable names to be included in the result.
            If not set, all variables are returned
        simulationnumber (int): number of simulation in the queue that should be
            run stepwise (default first simulation)

    Returns:
        VarMap : handle to simulation variables (possibly filtered). To access
        the variables, convert the result by varmapToList
    """
    par = _parameterListToArray(parameters)
    return simplaceInstance.stepSpecific(simulationnumber, par, varFilter,count)

def stepAllSimulations(simplaceInstance, count=1, parameterlist=None, varFilter=None):
    """
    Run all simulations in queue stepwise.

    Arguments:
        simplaceInstance: handle to the SimplaceWrapper object returned by
            initSimplace
        count (int): number of steps to perform
        parameterlist (list): a list of dictinaries with key-value pairs where
            the key has to match the Simplace SimVariable name
        varFilter (list): list of variable names to be included in the result.
            If not set, all variables are returned

    Returns:
        list : list of handles to simulation variables (possibly filtered).
        To access the variables, convert the items by varmapToList

    """
    par = _parameterListsToArray(parameterlist)
    return simplaceInstance.stepAll(par,varFilter,count)


# Fetch results and convert it to python objects.

def getResult(simplaceInstance, output, simulation=None):
    """
    Get a specific output of a finished simulation.

    If the parameter simulation is not given, the results
    of all simulation will be returned.

    Args:
        simplaceInstance: handle to the SimplaceWrapper object returned by
            initSimplace
        output (str): id of the memory output
        simulation (str): simulation id (optional)

    Returns:
        Result : handle to simulation output. To access the variables, convert
        the items by resultToList
    """
    return simplaceInstance.getResult(output, simulation)

def resultToList(result, expand=True, start=None, end=None, legacy=False):
    """
    Convert the output to a python dictionary

    Args:
        result: handle to simulation result (as returned by getResult())
        expand (bool): whether array values should be expanded to lists or
            kept as handles to java objects (optional)
        start (int): number of first entry to fetch (optional)
        end (int): number of last entry to fetch (optional)
        legacy (bool): if True, don't use numpy (optional)

    Returns:
        dict : simulation results as key-value pairs. Keys are the simulation
        variable nams, values are lists of simulated daily/yearly values
    """
    if(start is not None and end is not None and start <= end and start >= 0):
        obj =  result.getDataObjects(start, end)
    else :
        obj =  result.getDataObjects()
    names = [str(s) for s in result.getHeaderStrings()]
    types = [str(s) for s in result.getTypeStrings()]
    val = [_objectArrayToData(*z, expand=expand, legacy=legacy)
           for z in zip(obj, types)]
    return dict(zip(names, val))

def varmapToList(varmap, expand=True, legacy=False):
    """
    Convert the values of the last simulation step to a python dictionary.

    Args:
        varmap : handle to simulation varmap (as returned by stepSimulation())
        expand (bool): whether array values should be expanded to lists or
            kept as handles to java objects (optional)
        legacy (bool): if True, don't use numpy (optional)

    Returns:
        dict : simulation values as key-value pairs. Keys are the simulation
        variable nams, values are the values from last simulation step
    """
    names = [str(s) for s in varmap.getHeaderStrings()]
    obj =  varmap.getDataObjects()
    types = [str(s) for s in varmap.getTypeStrings()]
    val = [_objectToData(*z, expand=expand, legacy=legacy)
           for z in zip(obj,types)]
    return dict(zip(names, val))

def getUnitsOfResult(result):
    """
    Get the list of units of the output variables.

    Args:
        result: handle to simulation result (as returned by getResult())

    Returns:
        dict: dictionary where the variable names are keys and the units are the
        values

    """
    names = [str(s) for s in result.getHeaderStrings()]
    units = [str(s) for s in result.getHeaderUnits()]
    return dict(zip(names,units))


def getDatatypesOfResult(result):
    """
    Get the list of datatypes of the output variables.

    Args:
        result: handle to simulation result (as returned by getResult())

    Returns:
        dict: dictionary where the variable names are keys and the datatypes
        are the values

    """
    names = [str(s) for s in result.getHeaderStrings()]
    types = [str(s) for s in result.getTypeStrings()]
    return dict(zip(names,types))


# Configuration

def setSimplaceDirectories(simplaceInstance,
                           workDir = None, outputDir = None,
                           projectsDir = None, dataDir = None):
    """
    Set work-, output-, projects- and data-directory.

    Args:
        simplaceInstance: handle to the SimplaceWrapper object returned by
            initSimplace
        workDir (str): path to working directory
        outputDir (str): path to output directory
        projectsDir (str): path to projects directory
        dataDir (str): path to data directory
    """
    simplaceInstance.setDirectories(workDir, outputDir, projectsDir, dataDir)

def getSimplaceDirectories(simplaceInstance):
    """
    Get work-, output-, projects- and data-directory.

    Args:
        simplaceInstance: handle to the SimplaceWrapper object returned by
            initSimplace

    Returns:
        dict: dictionary with the actual paths for work-, outputdir etc.
    """
    names = ["_WORKDIR_", "_OUTPUTDIR_", "_PROJECTSDIR_", "_DATADIR_"]
    return dict(zip(names, [str(s) for s in simplaceInstance.getDirectories()]))

def setSlotCount(count):
    """
    Set the maximum numbers of processor cores used  when running projects.

    Args:
        count (int): maximal numbers of processor cores used.
    """
    jpype.JClass('net.simplace.sim.FWSimEngine').setSlotCount(count)

def setLogLevel(level):
    """
    Set the log's verbosity.  FATAL is least verbose, TRACE most verbose

    Args:
        level (str): possible values from least verbose 'FATAL' via 'ERROR',
            'WARN', 'INFO', 'DEBUG' to most verbose 'TRACE'
    """
    LOG = jpype.JClass('net.simplace.core.logging.Logger')
    LOGL = jpype.JClass('net.simplace.core.logging.Logger$LOGLEVEL')
    LOG.setLogLevel(LOGL.valueOf(level))

def setCheckLevel(simplaceInstance, level):
    """
    Set the checklevel of the solution. OFF does no checks,
    STRICT does most severe checks.

    Args:
        simplaceInstance: handle to the SimplaceWrapper object returned by
            initSimplace
        level (str): possible values: "CUSTOM,"STRICT","INTENSE","LAZY","OFF",
            "ONLY"
    """
    simplaceInstance.setCheckLevel(level)

def findSimplaceInstallations(directories=[],
        tryStandardDirs = True,
        firstMatchOnly = False,
        simulationsDir = "simplace_run",
        ignoreSimulationsDir = False,
        verbose = True    ):
    """
    Returns a list of simplace installations

    Args:
        directories (list): list of paths where to check for simplace
            subfolders
        tryStandardDirs (bool): check additionally for common standard locations
        firstMatchOnly (bool): return only the first matching directory
        simulationsDir (str): directory that contains user simulations
        ignoreSimulationsDir (bool): don't check for the simulations directory
        verbose (bool): print addtional messages

    Returns:
        list: List of paths to Simplace installations
    """
    parents = []
    home = os.environ.get('HOME')
    if(home!=None):
        parents = [home]
    parents += ["d:","c:","e:","f:","g:",os.getcwd()]
    subdirs = ["workspace/","simplace/","java/simplace/","simplace/workspace/"]
    dirs = directories
    if(tryStandardDirs):
        dirs = dirs + [p+"/"+s for p in parents for s in subdirs]
    required = {"simplace_core", "simplace_modules"}
    if(not ignoreSimulationsDir):
        required = required.union({simulationsDir})
    found = [d.rstrip("\\/")+"/" for d in dirs
            if os.path.exists(d)
            and required.issubset(set(os.listdir(d)))]
    if(verbose):
        if(len(found)==0):
            print("Could not detect Simplace automatically")
        if(firstMatchOnly and len(found)>1):
            print("Found more than one Simplace installation. Returning first one.")
    if (firstMatchOnly & len(found)>0):
        found = [found[0]]
    return found

def findFirstSimplaceInstallation(directories=[],
        tryStandardDirs = True,
        simulationsDir = "simplace_run",
        ignoreSimulationsDir = False):
    """
    Returns the path of the first simplace installation found

    Args:
        directories (list): List of paths where to check for simplace
            subfolders
        tryStandardDirs (bool): Check additionally for common standard locations
        simulationsDir (str): directory that contains user simulations
        ignoreSimulationsDir (bool): don't check for the simulations directory

    Returns:
        str: Path to first Simplace installation found
    """
    fl = findSimplaceInstallations(directories = directories,
                                   tryStandardDirs = tryStandardDirs,
                                   firstMatchOnly = True,
                                   simulationsDir = simulationsDir,
                                   ignoreSimulationsDir = ignoreSimulationsDir,
                                   verbose = False)
    return fl[0] if (len(fl)>0) else None



# Helper Functions


def _objectArrayToData(obj, simplaceType, expand = True, legacy = False):
    if legacy:
        return _objectArrayToDataOld(obj, simplaceType, expand)
    else:
        return _objectArrayToDataNew(obj, simplaceType, expand)

def _objectToData(obj, simplaceType, expand = True, legacy = False):
    if legacy:
        return _objectToDataOld(obj, simplaceType, expand)
    else:
        return _objectToDataNew(obj, simplaceType, expand)

def _objectArrayToDataOld(obj, simplaceType, expand = True):
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

def _objectToDataOld(obj, simplaceType, expand = True):
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



def _objectArrayToDataNew(obj, simplaceType, expand = True):
    if (simplaceType in ['DOUBLE','INT','BOOLEAN']):
        return numpy.array(obj)
    elif (simplaceType in ['DATE']):
        return [str(s)[:10] for s in obj]
    elif (simplaceType in ['CHAR']):
        return [str(s) for s in obj]
    elif expand and simplaceType in ['DOUBLEARRAY','INTARRAY']:
        return numpy.array(obj)
    elif expand and simplaceType in ['CHARARRAY']:
        return [[str(s) for s in row] for row in obj]
    else:
        return list(obj)

def _objectToDataNew(obj, simplaceType, expand = True):
    if (simplaceType in ['DOUBLE']):
        return obj.doubleValue()
    elif (simplaceType in ['INT']):
        return obj.intValue()
    elif simplaceType in ['DATE']:
        return str(obj)[:10]
    elif simplaceType in ['CHAR']:
        return str(obj)
    elif expand and simplaceType in ['DOUBLEARRAY','INTARRAY']:
        return numpy.array(obj)
    elif (simplaceType in ['CHARARRAY']):
        return [str(s) for s in obj]
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