See the documentation at https://simplace.readthedocs.io/

Run and control simulations in the simulation framework Simplace.

You need to install the Simplace simulation 
framework http://www.simplace.net/

Example usage:

    >>> import simplace
    >>> sh = simplace.initSimplace('/ws/','/runs/simulation/','/out/')
    >>> simplace.openProject(sh, '/sol/Maize.sol.xml')
    >>> simid = simplace.createSimulation(sh, {'vLUE':3.2,'vSLA':0.023})
    >>> simplace.runSimulations(sh)
    >>> result = simplace.resultToList(simplace.getResult(sh,'YearOut',simid))
    >>> simplace.closeProject(sh)
    >>> print(result['BiomassModule.Yield'])
    805.45
    
The module requires Java >= 8.0 and JPype1.
