
# si init

Initialize a si-managed project.

## Parameters

*	__-s__
	Creates a stand alone project. Any modules may be added freely to a stand alone project,
	but a stand alone project itself is not a git repository (and thus not using git
	submodules).
	Implies --no-bs and cannot be used together with -u

*	__-b [buildsystem]__
	Specifiy a build system for the project. All modules in the project must use the same
	build system. `si` currently only has support for cmake.

*	__-u [url]__
	This gives `si` the url to clone for the project. Cannot be used together with -s.

*	__-p [path]__
	The base path of the project to create. This path should either not exist or be empty.
	If this option is omitted, the current working directory is assumed.

*	__--no-bs__
	Postpone updating of build system files. This is useful, if you want to make changes to
	your configuration (i.e. add modules) before building the project.

## Examples

### Stand-Alone project

Given the 3 si-modules `bar`, `baz` and `frotz`, all of which are located at
`git@example.com:/`.
With `baz` having a dependency on `frotz`.

The sequence

	si init -s -p /work/foo
	si module add --no-bs -p /work/foo git@example.com:/bar.git
	si module add --no-bs -p /work/foo git@example.com:/baz.git
	si buildsystem update

will be equivalent to:

	mkdir -p /work/foo && cd /work/foo
	git clone git@example.com:/bar.git bar
	git clone git@example.com:/baz.git baz
	git clone git@example.com:/frotz.git frotz
	cp $SI_DIR/CMakeLists.txt.prefix CMakeLists.txt
	echo "ADD_SUBDIRECTORY(bar)" >>CMakeLists.txt
	echo "ADD_SUBDIRECTORY(frotz)" >>CMakeLists.txt
	echo "ADD_SUBDIRECTORY(baz)" >>CMakeLists.txt
	cat $SI_DIR/CMakeLists.txt.postfix >>CMakeLists.txt

si will:
-   setup the project directory
-   `git clone` the modules we explicitly added to it
-   figure out about the dependency from `baz` to `frotz` and will `git clone` `frotz`
-   scan the dependency graph and create a build system for your project


