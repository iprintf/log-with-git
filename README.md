A log program that can add, delete, edit, list and search entries, it syncs data with the server using git, all data that sent to the server are encrypted, plaintext data that is sensitive only exposed on the client side.

See LICENSE for license agreement.

See INSTALL for installation instructions.

2016-12-29:

kyo修改说明

    编辑结束对比文本否改变，如无改变则不做任何事

    由参数-i来控制是否交互收集信息(默认为不交互)

    收集的信息字段基本上都应该有默认值(默认值可通过配置文件来设置)

    由日志文件可以通过文件头信息来指定

    文件头前后模板可以通过配置来修改
        #LogInfo{
            字段名 = 字段值
            ...
        #LogInfo}

        如果没有文件头可以指定-i参数来交互设置
        如果没有文件头也没有指定-i则使用默认值(默认值可以通过配置文件设置)
        列表读取文件时不显示文件头信息

        添加
            命令参数指定日志信息则自动读取并设置文件头
            保存退出时:
                文件头存在则直接使用文件头的设置
                文件头不存在则使用命令参数指定日志的信息
                文件头不存在，命令参数也没有指定则使用默认值

        编辑
            打开文件时自动重新获取并生成文件头信息
            文件头存在则使用文件头的设置，文件头不存在则不改变日志信息字段

2016-12-30:

    TODO:
        修复editHeadInfo函数info字典如果字段不存在会报错

        使用全局变量保存配置信息

        log命令没有参数默认进入单行列表

        log edit命令没有参数默认编辑最后一条日志

        列表显示时处理连续空行问题
        列表显示只显示日志内容前10行
        当列表项只有一项时显示全部内容

        修复编辑命令参数错误进入到选择流程

        添加时只要有-m就直接保存不进入编辑嚣
            如果数据来源是管道或标准输入, 没有-m报错，有-m直接保存
            如果数据来源不是管道或标准输入，则-m有没有都要进入编辑嚣编辑

    遇到的问题:
        编辑时vim自动识别文件内容为mac平台(换行符是\r)导致保存格式有错
            vim可以通过set fileformat控制平台选择
                set fileformat=unix
            设置支持多平台的换行符: set fileformats=unix,mac,dos
            如果设置多平台时会自动选择, 有可能也会选择mac等

2016-12-31:

    TODO:
        添加配置指定什么编辑嚣(默认为vim)

        添加配置指定vim编辑嚣启动选项("+set ff=unix" "+set foldlevel=0")

        还原添加-m选项直接保存(即没有内容，只有标题的情况)
            -m可以指定标题和内容
            标准输入或管道可以与-m配合也可以单独指定标题和内容
            log add -m "title"
            log add -m $'title\n\ncontent'
            log add -m 'title\n\ncontent
            echo 'content' | log add -m 'title'
            echo 'content2' | log add -m 'title\n\ncontent1'
            echo 'title' | log add
            echo 'title\n\ncontent' | log add
            log add < file

        添加时增加-e选项，指定强制启动编辑嚣来编辑内容
            -m与-e选项同时存在则进入编辑嚣
            不管数据来源只要加-e选项都进入编辑嚣来编辑

            遇到的问题:
                管道右边启动vim，必须要加入-选项从标准输入获取数据 否则会报错
                如果加入-选项则不能指定编辑文件名，否则也会报错
                如果又想从标准输入获取数据，又要指定编辑文件路径
                方法一:
                    则可以将标准输入数据写入到编辑文件中
                    再关闭标准输入(0)文件描述符, 重新打开/dev/tty文件
                    再使用vim编辑写入数据的文件即可
                方法二:
                    将管道或标准输入的数据写入到临时文件中
                    vim加-选项, 追加选项: "+r临时文件路径" "+w!临时文件路径"
                    利用vim启动选项中执行vim命令行命令来完成

        添加支持管道或标准输入，编辑不支持管道或标准输入

        修改日志流程，处理编辑文件完成后程序原因导致保存失败问题
            如果程序原因保存失败则提供重新提交机制

            初始化生成一个运行标识符
            当运行编辑嚣时将临时文件路径加入到运行标识符生成锁文件
            正常退出将锁文件与临时文件删除
            非正常退出不会删除,并且将锁文件加.err后缀
            再次运行检测是否存在后缀为.err文件
            如果存在代表上一次存储失败, 提示错误进入修复交互
            修复交互:
                list        列表错误
                error       查看错误
                    cat errfile
                tmpfile     查看编辑(临时文件)
                    cat tmpfile
                source      查看日志(编辑失败的原日志)
                    log list ID
                delete      删除错误
                repair      自动修复(添加失败通过管道自动提交)
                    log add < tmpfile
                    log edit ID -r tmpfile
                open        重新编辑
                    log add -e < tmpfile
                    log edit ID -e -r tmpfile
                quit        退出交互

2017-01-01:

    TODO:
        完成修复交互的所有命令, 解决程序错误导致数据丢失问题

            遇到问题: /tmp目录的文件断电会丢失, 导致存储失败的数据丢失
            解决方法: 更换编辑嚣编辑使用临时文件的路径，合并运行文件
            处理流程:
                程序初始化时生成唯一临时文件名
                    临时文件名命名规则: 操作标识 + 随机标识
                        操作标识: 一个字符，A为添加 E为编辑
                        随机标识：  11位16进制数据
                            日志添加通过applib.genId来生成，取前11位
                            日志编辑取日志ID前6位 + 保留applib.genId生成的前5位

                当启动编辑嚣时:
                    进入程序运行目录(数据存储目录下的run文件夹)
                    在运行目录下创建临时文件并且打开进行编辑
                    编辑完成后关闭文件
                存储成功，程序正常退出删除临时文件
                存储失败:
                    程序异常捕获成功, 将错误信息写入错误日志文件
                        错误日志文件名与临时文件名一样，后缀为.err
                    不可预知程序中断则不会生成错误日志文件

            遇到的问题:
                vim编辑文件会改变inode，所以导致多方编辑数据无法同步
                vim编辑文件会给原文件改名再清空打开文件，所以导致inode不一致
                但如果编辑文件路径在/tmp目录下则不会出现此情况
                vim通过backupskip/nowritebackup选项可以控制

        启动日志程序检测是否有存储失败的文件
            如果有一个失败的文件询问是否尝试自动修复, 如果修复失败进入交互
            交互错误文件有多个的时候，进入选择流程(直接按回车代表选择最后一个)
            交互错误文件只有一个的时候，所有命令取消选择流程

        修改程序流程支持edit命令可以接受管道, 但只在修复交互下可用

2017-01-02:

    TODO:
        日志标题与内容的分割符为\n\n或\\n\\n
            重新封装分割标题与内容的函数splitSubject

        修复交互命令支持空回车顺序默认选择


2017-01-03:

    TODO:
        修改程序流程支持edit命令接受-r参数, 代表为编辑修复
            -r选项后必须跟一个文件(上一次编辑失败的文件)
            如果-r选项后没有有效路径才按正常编辑流程走
            编辑修复会将-r选项后的文件内容替换指定编辑日志, 默认不启动编辑嚣
            与-e配置使用可启动vimdiff来比较编辑

        log list查找失败没有错误码返回，无法识别是否正确
            修改list过滤嚣判断没有查找到数据，退出返回错误码为1

        正在编辑再启动Log会识别正在编辑为失败文件
            检验错误文件时加入查询进程列表条件
            判断错误文件是否在当前进程列表中，如果在则代表不是错误文件

            发现问题: python3 subpress.Popen执行特定shell命令报错
                ps -e --format cmd | grep E840dccbe5c3
                当终端宽度大于结果字符数，查询结果正常
                当终端宽度小于结果字符数，报错

        错误修复交互流程只有一个错误所有命令默认操作只能走一次
            原因是用了pop删除了列表，下次进来列表为空导致只能默认走一次流程

        不允许log edit同一个日志

2017-01-04:

    TODO:

        启动日志程序检测是否有存储失败的文件
            如果有一个失败的文件询问是否尝试自动修复
            交互错误文件只有一个的时候，所有命令取消选择流程

        发现问题: 通过管道或标准输入添加数据会多一个换行符
            ~/.viminfo文件会记录vim的命令行历史
                得到vim命令行历史的最后一条记录:
                    grep -m1 '^:' ~/.viminfo

        实现自动安装脚本

        实现加解密日志功能的脚本

2017-01-10:

    TODO:
        列表一个日志时不取消换行

        修改log clone流程
            检测xml目录是否存在，存在删除clone
            clone完成后再初始化log数据目录
            clone完成后自动合并数据到sqlite3中

        run目录创建增加判断条件，判断父目录是否存在，存在才创建

        del操作不会删除xml文件


2017-01-12:

    TODO:
        问题：管道或标准输入启动编辑器后退出不保存日志
        原因: 编辑器结束前与后的数据是否改变，如果没有改变则退出
        解决：判断是管道或标准输入编辑模式时，vim最后以wq退出则不对比

        实现加解密日志功能的脚本

2017-01-13:

    TODO:
        增加note脚本的添加与编辑命令首字母简称

2017-01-16:

    TODO:
        完善加密脚本功能
            参数的检查与容错
            支持环境变量控制配置文件路径

        修改kdy脚本支持多日志编辑

        kdy脚本增加只读编辑(查看功能)

        问题:
            kdy脚本添加获取文件第一行做标题
            如果此行有空格则只能获取空格前内容
        原因: 将参数组合在一个变量里导致
        解决: 将参数单独存放在一个变量，传参时加双引号

2017-01-17:

    TODO:
        增强kdy脚本功能，合并加密库与普通库
            增加加密添加命令(en)
            增加解密编辑命令(edit/e 通用普通编辑及解密编辑)
            增加tag查询命令
            增加read只读命令
            第一个参数是sha1值,直接调用edit来操作

2017-01-18:

    TODO:
        修复参数带引号传入失效问题(对所有$@打双引号解决)

        增强kdy tag命令功能
            修改tag命令默认功能，对所有日志tag进行去除统计
            增加tag --all / tag -a选项统计所有日志tag(会处理逗号分隔符)
            扩展tag查找功能，如果有一条记录则直接启动编辑,多条则列表选择(未完成)

        增加list命令显示格式参数%tk(创建时间格式化)

    BUG:
        read命令对普通日志没有起到只读作用
        编辑最后一条日志时，添加新日志退出，再保存编辑日志会覆盖添加的日志

2017-01-19:

    TODO:
        增加环境变量控制vim编辑器启动选项
        修复read命令对普通日志没有起到只读作用
        修复编辑最后一条日志与添加新日志的冲突问题
        完善kdy tag命令功能支持自动打开编辑或选择编辑
