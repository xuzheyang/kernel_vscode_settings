# cfg2set.py

网上的 Linux 驱动的开发环境搭建比较困难，通过几天的资料查询，找到了一天通路，记录并脚本化。
通过 Linux kernel config 文件与交叉编译工具链的环境设置 VSCode。

## 设置交叉编译工具链

在运行之前需要先设置交叉编译工具链，也不是必须的，如果没有检测到交叉编译工具链的话会使用当前的系统的 gcc

```shell
export ARCH="arm" # or x86_64 / mips64el / loongarch64
export CROSS_COMPILE="arm-xuzheyang-linux-gnueabihf-"
export PATH="$PATH:/imx6ullpro/arm_cross_toolchain/bin"
```

## 编译内核

脚本中需要用到内核的配置文件，所以需要先配置内核：

```shell
make xxxx_xxxx_config
```

之后的内核编译可以不进行，但是会有配置好环境后函数跳转会提示找不到符号，所以建议编译一遍

```shell
make -j8
```

## 最后运行脚本添加 VSCode 配置

需要安装 VSCode 插件 C/C++ Extension Parck，如果是通过 Remote - SSH 连接的话，需要把插件安装在远端。VSCode 的读取优先级应该是先项目，后全局。下面的方式设置一种即可：

### 设置本地 VSCode 配置文件

直接本地打开 VSCode 时的全局配置

```shell
python3 cfg2set.py -l /path/to/kernel
```

### 设置远端 VSCode 配置文件

通过 Remote - SSH 插件连接到本机时 VSCode 的全局配置

```shell
python3 cfg2set.py -s /path/to/kernel
```

### 设置项目 VSCode 配置文件

每个项目单独的配置

```shell
python3 cfg2set.py -p /path/to/kernel /path/to/project
```
