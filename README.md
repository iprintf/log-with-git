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

        添加支持管道或标准输入，编辑不支持管道或标准输入

        保存日志时判断标题和内容是否相同，相同则更新存在数据的修改时间

        修改日志流程，处理编辑文件完成后程序原因导致保存失败问题
            如果程序原因保存失败则提供重新提交机制

