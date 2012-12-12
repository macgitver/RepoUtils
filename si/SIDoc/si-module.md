
# si module

Manage the modules that a si-project contains.

## Usage

	si module list   [-p path]
	si module add    [-p path] [--no-bs] [-b branch] url name
	si module create [-p path] [--no-bs] name
	si module del    [-p path] [--no-bs] [-f | --force] name
	si module update [-p path] [--no-bs] name | -a

## Subcommands

### list

Output a list of currently known modules.

#### Parameters

*	__-p path__
	The base path of the si-project.

### add

Add a new module to a si-project.

#### Parameters

*	__-p path__
	The base path of the si-project.

*	__--no-bs__
	Postpone updating of build system files. This is useful, if you want to make changes to
	your configuration (i.e. add more modules) before building the project.

*	__-b branch__
	Registers the named branch with si. 
	If a branch is registered with si, any cloning, fetching or submodule update will use that
	branch. But note, that as of today, git submodule will not handle following branches on its
	own correctly.

*	__url__
	The url from which to `git clone` the code for the newly added module.

*	__name__
	The name of the new module. In most cases this will be the same as the repository name.

If the si-project is a standalone project, a simple `git clone` will be executed. If on the
other hand, the si-project is a git managed project itself, a submodule will be added to the
si-project. It will be initialized and cloned.

### create

Create an empty shell for a new si-module.

### del

Remove a si-module from a si-project.

-

If a si-module is required by another si-module as a dependency, an error is given. Use `-f` or
`--force` to force the removal of the si-module. However, any subsequent dependency scan will
result in errors unless the dependency mismatch is clean up first.

### update

Update a si-module.
