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
                    cat tmpfile | log add
                open        重新编辑
                    cat tmpfile | log add -e
                    cat tmpfile | log edit ID
                quit        退出交互

        保存日志时判断标题和内容是否相同，相同则更新存在数据的修改时间
