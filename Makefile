###############################################################################
#
# Makefile for a Python script, project 10
#
# Students:
# Guy Pelc, ID 203552823, guy.pelc@mail.huji.ac.il
#
#
###############################################################################

# This is a sample makefile. 
# The purpose of makefiles is to make sure that after running "make" your project is read for execution.
# Usually, scripting language (e.g. Python) based projects only need execution permissions for your run 
# file executable to run. The executable for project 6 should be called Assembler.
# Obviously, your project may be more complicated and require a different makefile.
# For this file (Makefile-script) to run when you call "make", rename it to "Makefile".

# The following line is a rule declaration. A makefile rule is a list of prerequisites (other rules that 
# need to be run before this rule) and commands that are run one after the other. The "all" rule is what 
# runs when you call "make":
all:
	chmod a+x JackAnalyzer

# As you can see, all it does is grant execution permissions for your run time executable, so your project 
# will be able to run on the graders' computers. In this case, the "all" rule has no preqrequisites.

# A general rule looks like this:
# rule_name: prerequisite1 prerequisite2 prerequisite3 prerequisite4 ...
#	command1
#	command2
#	command3
#	...
# Where each preqrequisite is a rule name, and each command is a command-line command (for example chmod, 
# javac, echo, etc').