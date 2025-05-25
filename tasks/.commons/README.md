# Task Commons Repository

This repository
 is generally used
 as a submodule
 in task repositories.
The files/directories here
 are going to be referred and used
 in the task repository
 through symbolic links.

Though,
 the `.gitignore` file
 is an exception.
Naturally,
 we wanted to put
 a common `gitignore` file here
 which is referred
 (using a symbolic link)
 by the `.gitignore` file
 in the task repository.
But,
 this idea did not work
 because
 Git does not follow symbolic links
 when accessing a `.gitignore` file
 in the working tree.
So,
 we manually copy
 the `.gitignore` file of the task repository
 from `<TPS-REPO>/extra-assets/problem.gitignore`.
