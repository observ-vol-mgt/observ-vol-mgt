# Controller

The controller is tasked with overseeing the management of the volume of observability data across the processors and collectors. It does this by analyzing the behavior of observability signals and correlating them with customer requirements and the usage of signals in the system. Based on this analysis, the controller generates recommendations and automatically updates configurations to manage and reduce the volume of observability data.

## architecture

The controller architecture is described at [docs/architecture.md](docs/architecture.md) 

## How to run

To run the code, use the provided Makefile.

For detailed execution options, use `make help`

