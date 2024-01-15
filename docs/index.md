# ARCHIVED 
# YChaos

YChaos is a self-serving chaos testing toolkit designed to
provide you with all the capabilities of doing an end to end resilience
testing of your service. YChaos is designed to give users a framework
to validate, verify and attack your system to simulate real life
failures that might cause outages in your service.

The real life failures/attacks are termed as [Agents](agents/index.md) in
YChaos' terminology. Agents are the independent attack scenarios
that perform one kind of attack on the system with a specified configuration.

YChaos also provides a way to verify your system state before, during and after
the completion of attack. This ensures that you as a user are in control
when to perform attack and also provides you a detailed report as to what went
wrong with your service during the attack so that you can apply corrective
measures to ensure that your service is resilient.

### What is true about YChaos?

1. YChaos is a resilience testing tool.
2. YChaos is a self serving tool. You as a user of YChaos control
the entire infrastructure of attacking your systems. Hence, you need not
worry about a third party system controlling your systems.
3. YChaos can be integrated with popular CI/CD platforms 
such as [Screwdriver](https://screwdriver.cd/)

### Some fact checks about YChaos!

1. YChaos is not a Load testing tool.
2. YChaos does not automatically address the issues in your service. YChaos
provides you a way to identify issues in your service
3. YChaos does not need any daemon running on your services.

### Project architecture

[View this diagram](resources/img/executor_flowchart.svg) if you are interested in knowing the YChaos
Project architecture.

## Installation

You can install the package using pip or directly from Github

=== "Artifactory"

    ```bash
    pip install ychaos[chaos]
    ```
    
    The above command will install the latest version of the `chaos` sub-package
    from artifactory. To install another subpackage of `ychaos`, 
    
    ```bash
    pip install ychaos[<subpackage>]
    ```

    The following subpackages are available for usage
    
    1. agents : `pip install ychaos[agents]`
    2. chaos : `pip install ychaos[chaos]`
   
=== "Source"

    You can also install the package directly from source. To do this,
    
    ```bash
    git clone https://github.com/yahoo/ychaos
    cd ychaos
    python setup.py develop easy_install ychaos[<subpackage>]
    ```

If you are interested in installing all the above subpackages together,
you can run

```bash
pip install ychaos[all]
```

YChaos tool can be used with python3.6+ and must have pip3 pre-installed

## Docker hub

Python version specific YChaos images are published with each release of YChaos, at present Python `3.7`-`3.9` 
based images are available on [Docker hub](https://hub.docker.com/r/ychaos/ychaos).

=== "Docker"
    ```bash
    docker pull ychaos/ychaos
    ```

    Above command will pull the latest Python 3.6 based YChaos image. 
    For any other Python version specific images use

    ```bash
    docker pull ychaos/ychaos:py<version>-latest
    ```

    Refer [Docker tags](https://hub.docker.com/r/ychaos/ychaos/tags) 
    for all the available Image tags
