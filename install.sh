#!/bin/bash

myexit() {
    echo $1
    exit $2
}

getname() {
    dir=${1-~}
    name="$(echo $(date +%s)$[1999 + RANDOM % 8000] | sha1sum | base64)"
    name="$dir/.kyo_log_${name:5:10}"
    echo $name
}

creat_dir() {
    test ! -e "$datadir" && mkdir -p "$datadir"
    test ! -e "$datadir/run" && mkdir "$datadir/run"
}

creat_conf() {
    cat > $rcfile << EOF
# vim: filetype=python:
#
# These code is Python code.
# Only variable assignment will be retained

# Where to store the log data
dataDir = '$datadir'

# Author name
authorName = 'Long Zhu'

# Author email
authorEmail = 'iprintf@qq.com'

#  默认字段信息定界符
infoDelim = '# Log Info {\n%s\n# Log Info }'

#  默认地点
defaultScene = 'ShenZhen'

#  默认人物字段
defaultPeople = 'kyo'

#  默认Tag
defaultTag = 'undefined'

#  默认列表显示内容行数
listCL = 10

#  默认编辑嚣
editor = 'vim'

#  vim编辑嚣的打开选项
vimOpt = '"+set ff=unix" "+set foldlevel=0"'
EOF
}

do_install() {
    test -e "$rcfile" && myexit "$rcfile, 指定的配置文件已经存在!"
    test -d "$datadir" && myexit "$datadir, 指定的数据目录已经存在!"
    creat_dir
    creat_conf
    /bin/cp repair.vim "$datadir/run/"
    test -e /usr/local/bin/note || ln -s "$(pwd)/main" /usr/local/bin/note
    test -e /usr/local/bin/kdy || ln -s "$(pwd)/note" /usr/local/bin/kdy
    log -F $rcfile
}

rcfile=${1-~/.logrc}
datadir=${2-$(getname)}
# datadir=$(getname "/tmp")
# rcfile='/tmp/logrc'

echo $datadir
echo $rcfile

do_install
