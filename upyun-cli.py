#!/usr/bin/env python3
import os
import sys
from datetime import datetime

import click
import colorama
import upyun
import yaml
from colorama import Back
from colorama import Fore
from colorama import Style
from progressbar import ProgressBar
from upyun import UpYun
from upyun import UpYunServiceException

configure = None
configure_file = None
Upyun = None

colorama.init()


def show_title(title): click.echo(
    (Back.LIGHTBLUE_EX + Fore.LIGHTWHITE_EX + "%s" + Fore.RESET + Back.RESET) % str.strip(title))


def show_error(msg):
    click.echo(Fore.LIGHTWHITE_EX + Back.RED + msg + Back.RESET + Fore.RESET)


def get_readable_date(time_stamp, format='%Y-%m-%d %H:%M:%S'):
    d = datetime.fromtimestamp(int(time_stamp))
    return d.strftime(format)


def show_file(name, type='file', size=0, time=0):
    if type == 'folder':
        name = (Fore.BLUE + "[{:s}]" + Fore.RESET).format(name)
    meta = get_readable_date(time)
    if size > 0:
        meta += (Style.BRIGHT + "{:>8.2f}MiB").format(size)
    meta = Style.DIM + meta + Style.RESET_ALL
    click.echo("%s %s" % (meta, name))


class ProgressBarHandler(object):
    def __init__(self, totalsize, params):
        self.bar = ProgressBar(max_value=totalsize)

    def update(self, readsofar):
        self.bar.update(readsofar)

    def finish(self):
        self.bar.finish()


@click.group()
@click.option('--config-file', help="指定配置文件的路径，默认在 ~/.upyun-cli.yml")
def cli(config_file):
    """基于又拍云 Python SDK(https://github.com/upyun/python-sdk) 的命令行工具"""
    try:
        global Upyun
        load_config(config_file)

        # 载入配置
        bucket, network = configure.get("bucket"), configure.get('network')

        # 使用配置链接到又拍云
        Upyun = UpYun(bucket['name'],
                      username=bucket['user'],
                      password=bucket['password'],
                      timeout=network['timeout'],
                      endpoint=upyun.ED_AUTO)
    except FileNotFoundError as error:
        show_error("The file %s is not found." % config_file)
        sys.exit(error.errno)
    except Exception as error:
        show_error("Some bad things is happened.")
        sys.exit(-1)


def load_config(file=None):
    """根据指定的文件引入配置，配置文件的格式为 YAML，如果为空则使用默认路径"""
    global configure, configure_file

    # 默认文件路径在用户主目录下
    default_config_file = os.path.expanduser("~") + os.path.sep + ".upyun-cli.yml"

    if file is None:
        file = default_config_file

    if not os.path.exists(file):
        raise FileNotFoundError("Error The config file %s is not exists." % file)

    configure_file = file
    try:
        configure = yaml.load(open(configure_file, "r"))
    except Exception:
        raise FileNotFoundError("Parse error, please check your config file %s" % file)


@cli.command()
@click.argument('src', nargs=-1, type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.argument('dst', nargs=1, default="/")
@click.option("--show-progress/--no-progress", default=True, help="显示（隐藏）上传进度条")
def put(src, dst, show_progress):
    """上传文件到远程 Bucket，同时返回 URL 地址"""
    # 去除重复 @see https://www.cnblogs.com/infim/archive/2011/03/10/1979615.html
    src = list(set(src))
    progress = ProgressBarHandler if show_progress is True else None
    if len(src) is 0:
        show_error("必须指定需要上传的文件以及远程路径")
        return

    for i in src:
        if os.path.isfile(i):
            if len(src) > 1:
                key = os.path.join(dst, os.path.basename(i))
            else:
                key = dst

            try:
                with open(i, 'rb') as f:
                    result = Upyun.put(key, f, handler=progress, checksum=True)
                    # click.echo(result)

                    # @todo 需要更好的 Url 组合
                    url = (configure.get("url")["host"] + key)
                    click.echo(url)
            except UpYunServiceException as e:
                show_error(e.msg)


@cli.command()
def info():
    """获取 SDK 以及 Bucket 相关的信息"""
    click.echo("Upyun SDK v%s" % upyun.__version__)
    show_title("Loaded configure: %s\n" % configure_file)

    bucket, network = configure.get("bucket"), configure.get('network')
    click.echo("  Bucket: %s" % bucket['name'])
    click.echo("Operator: %s" % bucket['user'])

    try:
        usage = float(Upyun.usage())
        click.echo("   Usage: %1.2fMiB" % (usage / 1024 / 1024))
    except UpYunServiceException as e:
        show_error(e.msg)


@cli.command()
@click.argument('path', nargs=-1)
@click.option('--prompt', prompt='Are you sure?', default="n", help="是否确认删除信息，指定 yes 则不提醒")
def rm(path, prompt):
    """删除 Bucket 中的文件或者目录"""
    prompt = str(prompt).lower()
    if prompt == "y" or prompt == "yes":
        try:
            for file in path:
                Upyun.delete(file)
                click.echo(file + " is deleted")
        except UpYunServiceException as error:
            show_error(error.msg)


@cli.command()
@click.argument('path', default="/", nargs=1)
@click.option('--order', default='asc', help='The list of Order')
def ls(path, order):
    """显示文件或者目录的详细信息"""
    try:
        res = Upyun.getinfo(path)

        show_title("{} [{}]".format(res['file-type'].capitalize(), path))
        if res['file-type'] == 'folder':
            items = Upyun.iterlist(path, limit=100, order=order, begin=None)
            for item in items:
                file_size = float(item['size']) / 1024 / 1024
                file_type = 'folder' if item['type'] == 'F' else 'file'
                show_file(name=item['name'], type=file_type, size=file_size, time=item['time'])
        elif res['file-type'] == 'file':
            file_size = float(res['file-size']) / 1024 / 1024
            show_file(name=path, size=file_size, time=res['file-date'])
        else:
            show_error("%s not exists" % path)
    except UpYunServiceException as error:
        show_error(error.msg)


@cli.command()
@click.argument('path', nargs=-1)
def purge(path):
    """额外提交刷新请求，基于 Url 地址"""
    # 去除重复 @see https://www.cnblogs.com/infim/archive/2011/03/10/1979615.html
    path = list(set(path))
    for file in path:
        try:
            result = Upyun.purge(file)
            if len(result) > 0:
                show_title(file + " is purged")
            else:
                raise FileNotFoundError
        except UpYunServiceException as error:
            show_error(error.msg)
        except FileNotFoundError:
            show_error(file + ' has not purged')


@cli.command()
@click.argument('src', nargs=-1)
@click.argument('dst', nargs=1, type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option("--show-progress/--no-progress", default=True, help="显示（隐藏）下载进度条")
def get(src, dst, show_progress):
    """从远程获取文件到本地"""
    progress = ProgressBarHandler if show_progress is True else None
    for remote_path in src:
        try:
            res = Upyun.getinfo(remote_path)
            if res['file-type'] == 'file':
                save_file = os.path.expanduser(dst + os.path.sep + os.path.basename(remote_path))
                with open(save_file, 'wb') as f:
                    Upyun.get(remote_path, f, handler=progress)
                show_title("{0} => {1}".format(remote_path, save_file))
            else:
                raise FileNotFoundError
        except UpYunServiceException as e:
            show_error("The file " + remote_path + " is " + e.msg)
        except FileNotFoundError:
            show_error(remote_path + " is not a file")
        except PermissionError:
            show_error("Can not write file")
    pass


@cli.command()
def web():
    """打开本脚本的 github 主页"""
    url = "https://github.com/feelinglucky/upyun-cli.py"
    import webbrowser
    webbrowser.open(url)


@cli.command()
def config():
    """显示已载入的配置信息"""
    show_title("Loaded configure: %s\n" % configure_file)
    click.echo(yaml.dump(configure))


if __name__ == '__main__':
    try:
        cli()
    except Exception as e:
        show_error(e)
