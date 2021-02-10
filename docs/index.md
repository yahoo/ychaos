

## Installation

You can install the package using pip or directly from Github

=== "Artifactory"

    ```bash
    pip install vzmi.ychaos[chaos]
    ```
    
    The above command will install the latest version of the `chaos` sub-package
    from artifactory. To install another subpackage of `vzmi.ychaos`, 
    
    ```bash
    pip install vzmi.ychaos[my-awesome-subpackage]
    ```
    
    To see all the subpackages available in the toolkit, refer to the documentation
    about subpackages [here](subpackages.md)
   
=== "Source"

    You can also install the package directly from source. To do this,
    
    ```bash
    git clone git@git.vzbuilders.com:resilience/vzmi.ychaos.git
    cd vzmi.ychaos
    python3 setup.py install
    ```
