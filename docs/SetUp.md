# Set Up
In order to install all project dependencies (including the website dependencies) run `make setup` in root direcory.

If you don't need website interface, run `make setup-basic` - it will skip installation of some packages like FastAPI.
Local start up of the website is described [here:](./website/Website.md)

## Other usefull commands
* linting: `make lint` (using black for Python and prettier for TypeScript)
* test: `make test`
