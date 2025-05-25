#git rm --cached -r .commons
#rm -rf .commons
#git submodule add --force git@github.com:Olimpiada-Boliviana-De-Informatica/task-commons.git .commons
#git rm --cached -r .commons
#git config -f .gitmodules --remove-section submodule..commons
#git add .gitmodules
#rm -rf .git/modules/.commons

prepare_folder() {

  cd tasks || exit

  for task_name in "$@"; do
    echo "Task: $task_name"
    mkdir -p "$task_name"

    cd "$task_name" || exit
    mkdir -p checker gen validator statement solution grader public

    echo '  linking scripts ...'
    rm -rf scripts
    ln -s ../.commons/tps-scripts scripts

    echo '  linking files into "checker" folder ...'
    mkdir -p checker
    cd checker || exit
    rm -rf Makefile
    ln -s ../../.commons/Makefile Makefile
    rm -rf testlib.h
    ln -s ../../.commons/testlib.h testlib.h
    cd .. || exit

    echo '  linking files into "gen" folder ...'
    mkdir -p gen
    cd gen || exit
    rm -rf Makefile
    ln -s ../../.commons/Makefile Makefile
    rm -rf testlib.h
    ln -s ../../.commons/testlib.h testlib.h
    cd .. || exit

    echo '  linking files into "validator" folder ...'
    mkdir -p validator
    cd validator || exit
    rm -rf Makefile
    ln -s ../../.commons/Makefile Makefile
    rm -rf testlib.h
    ln -s ../../.commons/testlib.h testlib.h
    cd ..

    echo "  linking files of statement"
    mkdir -p statement
    cd statement || exit
    rm -rf assets
    ln -s ../../.commons/md-viewer/assets assets
    rm -rf index.html
    ln -s ../../.commons/md-viewer/index.html index.html
    rm -rf index.json
    ln -s ../problem.json index.json
    cd .. || exit

    cd ..
  done
  cd ..
}

prepare_folder "$@"
