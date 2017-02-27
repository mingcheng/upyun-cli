基于又拍云 Python SDK 的命令行工具
##################################

..
 .. image:: https://badge.fury.io/py/upyun-cli.png
    :target: https://badge.fury.io/py/upyun-cli
    :height: 20px
.. image:: https://travis-ci.org/feelinglucky/upyun-cli.py.svg?branch=master
    :target: https://travis-ci.org/feelinglucky/upyun-cli.py
    :height: 20px

特性
####

.. image:: https://gracecode.b0.upaiyun.com/2016_12_03/1480756208.png!w700
    :width: 700px

* 完整的命令行功能支持
* 直观的界面，支持颜色高亮
* 上传下载进度条显示
* 支持批量更新处理


安装
####

可以直接使用 pip 安装 ::

    pip install upyun-cli

或者从 https://github.com/feelinglucky/upyun-cli.py 手工下载源代码，运行 ::

    python3 upyun-cli.py

PS，实际上整个项目的核心脚本就这一个，很方便部署。

配置
####

默认配置文件在 ``$HOME/.upyun-cli.yml`` 下， `Yaml <http://yaml.org>`_ 格式。编辑这个文件内容::

    bucket:
        name: <bucket-name>
        user: <operator>
        password: <password>

    url:
        host: <bucket-host>

bucket 中的信息分别对应填写，其中 url 节点的是您绑定域名的地址。

例如在 bucket 中 ``/file`` 的路径映射的是 ``http://files.gracecode.com/file`` 那么就填写 ``http://files.gracecode.com`` 。

同时，在运行期间还可以指定另外的配置文件地址，加上对应的参数方便切换 bucket 例如 ::

    upyun-cli.py --config-file=<path_to_file>


测试
####

upyun-cli 使用多个子命令构成，相互独立不受影响。我们配置完成了以后就可以直接
使用脚本了。::

    upyun-cli.py config

就可以看到已经载入的配置文件路径以及配置内容，然后可以简单的查看 bucket 信息就可以知道配置是否正确。::

    upyun-cli.py info

如果一切正常，就看到相关的信息了。


使用
####

显示文件和目录
--------------

默认显示带有高亮的文件和目录列表 ::

    upyun-cli.py ls <remote-file/remote-folder>

默认为 bucket 的根 "/" 目录


上传
----

上传文件支持批量上传，如果是单个文件，则默认最后个指定的为 url 地址。例如::

    upyun-cli.py put [files] <remote-folder>

则文件会上传到 ``<remote-dir>/[files]`` 下面，而::

    upyun-cli.py put <file> <remote-path>

则会上传到 ``<remote-path>`` 为 url 的地址下。因此如果上传单个文件，则请务必指定实际的 url 地址。


下载
----

下载操作和上传操作类似，但有唯一的不同是最后的本地地址参数一定要是目录，并且有写入的权限。::

    upyun-cli.py get [remote-files] <local-folder>


删除
----

删除远程目录务必主要注意目录必须为空，出于安全方面的考虑并没有实现递归删除的功能。::

    upyun-cli.py rm [remote-files/remote-folder]


更新缓存
--------

除非覆盖了远程的同名文件，一般不需要强制刷新缓存::

    upyun-cli.py purge [remote-files/remote-folder]


常见问题
########

Q: 有没有在 Python2 下测试过
----------------------------
A: 不好意思，一直用 Python3 了


更新日志
########

``2017-02-27`` 修复初始化状态配置文件显示 None 的问题
``2016-12-15`` 增加持续集成服务
``2016-12-03`` 发布第一个公开版本

