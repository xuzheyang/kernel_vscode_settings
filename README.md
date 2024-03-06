# cfg2set.py

通过 Linux kernel config 文件与交叉编译工具链的环境设置 VSCode

## 设置交叉编译工具链

在运行之前需要先设置交叉编译工具链：

```shell
export ARCH="arm" # or x86_64 / mips64el / loongarch64
export CROSS_COMPILE="arm-xuzheyang-linux-gnueabihf-"
export PATH="$PATH:/imx6ullpro/arm_cross_toolchain/bin"
```

## 编译内核

内核中许多目录是编译时生成的，所以需要先编译：

```shell
make xxxx_xxxx_config
make -j8
```

## 最后运行脚本添加 VSCode 配置

需要安装 VSCode 插件 C/C++ Extension Parck，VSCode 的读取优先级应该是先项目，后全局

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
