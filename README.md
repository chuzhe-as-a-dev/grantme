# grantme

```console
$ grantme
################################################################################
The machine is free.
Get access with `grantme --mode {shared,exclusive} --duration ?d?h?m?s`.
################################################################################

$ grantme --mode shared --duration 2h
Granted shared access to tang until 2026-11-01 20:16 (2h left).

$ grantme --mode exclusive --duration 3h
Upgraded tang's access to exclusive until 2026-11-01 21:16 (3h left).

$ grantme
################################################################################
EXCLUSIVE access is held by:
  tang (you)  until 2026-11-01 21:16 (3h left)
################################################################################

$ grantme --revoke
Revoked tang's exclusive access.
```

## English

`grantme` is a lightweight machine access management CLI tool written in Python.
It can grant timed *shared access* (e.g., for debugging) and *exclusive access* (e.g., for performance evaluation) to individual users so that users of shared machines can coordinate their usage.
It is noncompulsory and purely advisory because it cannot prevent malicious users from ignoring the access granted.

### Usage

#### Rules

1. When no access is granted, users can request either shared or exclusive access.
2. When some shared access is granted, other users can request additional shared access.
   When there is only one user granted with shared access, that user can upgrade his/her access to be exclusive.
3. When exclusive access is granted, other users cannot request any access.
4. Granted access expires after given duration.
   Users with granted access can early revoke or prolong their access.

#### Return values

`grantme` returns values according to operation results.

- 0: Success
- 6: Failed to upgrade access
- 7: Failed to obtain access
- 255: Other errors

These return values can be used for integrating `grantme` into other scripts (e.g., automatic testing).

```shell
#!/bin/bash

grantme --mode exclusive --duration 1h
if [ $? -ne 0 ]
then
    echo "Can't get the lock."
    exit 1
fi

# do work

grantme --revoke
```

#### Requirements

`grantme` requires Python 3.5+, with no third-party dependencies and no root privilege.

#### Installation and uninstallation

The maintainer clones this repository to a location readable by all users (denoted `<GRANTME_HOME>` below), updates it there with `git pull`, and runs `grantme --init` once on each machine to create the database.
The database resides in `/scratch/grantme` by default and is readable and writable to all users.
To place it elsewhere, copy `bin/grantme.conf.example` to `bin/grantme.conf` (untracked by git) and set `data_dir` under `[default]` or under a section named after a host to override that host only.

```shell
git clone <REPO_URL> <GRANTME_HOME>
<GRANTME_HOME>/bin/grantme --init  # once per machine
```

Each user adds the following to `~/.bashrc` to use `grantme`:

```shell
export PATH="<GRANTME_HOME>/bin:$PATH"
```

To automatically print access status upon login on Ubuntu, the system administrator links the update-motd fragment on each machine (requires root):

```shell
ln -s <GRANTME_HOME>/contrib/99-grantme /etc/update-motd.d/99-grantme
```

Without root, each user can instead add `[ -t 1 ] && grantme --status` to `~/.bashrc`.

To uninstall, remove `<GRANTME_HOME>`, the data directory, `/etc/update-motd.d/99-grantme`, and the lines in each user's `~/.bashrc`:

```shell
rm -rf <GRANTME_HOME> /scratch/grantme
rm /etc/update-motd.d/99-grantme  # requires root
```

### Contribute

Currently, `grantme` is maintained by an individual.
Bug reports and pull requests are welcomed.

#### Testing

Execute the following command in the project's root directory to run tests.

```shell
python -m unittest discover
```

Please add or modify test cases under the `tests` directory when adding new features or fixing bugs.
Make sure all tests have passed before submitting pull requests.

## 中文

`grantme`是一个用Python写的轻量级机器访问管理命令行工具。它可以授权用户一定时限内的共享访问权限（如，用于debug）和独占访问权限（如，用于性能测试），从而共享同一台机器的用户可以协调机器使用。它是非强制、纯建议性的，因为它不能防止恶意用户无视访问权限授权地使用机器。

### 使用方式

#### 规则

1. 当未授权任何访问权限时，用户可任意获取共享或独占权限。
2. 当已授予共享访问时，未授权用户可获取共享权限。若仅一位用户被授予共享权限，该用户可升级其为独占权限。
3. 当已授予独占访问时，未授权用户不可获取任何权限。
4. 权限在过期后自动失效。已授予权限的用户可提前放弃或延长所持有权限。

#### 返回值

`grantme`根据操作结果返回相应值。

- 0：成功
- 6：升级权限失败
- 7：获取权限失败
- 255：其他错误

这些返回值可用于将`grantme`集成到其他脚本（如，自动化测试）。

```shell
#!/bin/bash

grantme --mode exclusive --duration 1h
if [ $? -ne 0 ]
then
    echo "Can't get the lock."
    exit 1
fi

# do work

grantme --revoke
```

#### 依赖

`grantme`要求Python 3.5及以上版本，无需安装第三方依赖，也无需root权限。

#### 安装与卸载

管理者将本仓库克隆到一个所有用户可读的位置（以下记为`<GRANTME_HOME>`），更新时在该处`git pull`即可，并在每台机器上运行一次`grantme --init`以创建数据库。数据库默认位于`/scratch/grantme`，对所有用户开放读写。如需放在别处，将`bin/grantme.conf.example`复制为`bin/grantme.conf`（不纳入git），并在`[default]`节或以主机名命名的节（仅覆盖该主机）中设置`data_dir`。

```shell
git clone <REPO_URL> <GRANTME_HOME>
<GRANTME_HOME>/bin/grantme --init  # 每台机器一次
```

每位用户在`~/.bashrc`中加入以下内容，以使用`grantme`：

```shell
export PATH="<GRANTME_HOME>/bin:$PATH"
```

如需在Ubuntu上于用户登录时自动打印授权状态，由系统管理员在每台机器上链接update-motd脚本（需要root权限）：

```shell
ln -s <GRANTME_HOME>/contrib/99-grantme /etc/update-motd.d/99-grantme
```

若无root权限，也可由每位用户在`~/.bashrc`中加入`[ -t 1 ] && grantme --status`。

卸载时删除`<GRANTME_HOME>`、数据目录、`/etc/update-motd.d/99-grantme`以及各用户`~/.bashrc`中的对应行：

```shell
rm -rf <GRANTME_HOME> /scratch/grantme
rm /etc/update-motd.d/99-grantme  # 需要root权限
```

### 参与开发

目前，`grantme`由个人维护。欢迎用户提交缺陷报告和Pull Request。

#### 测试

在项目根目录下执行以下命令以运行测试。

```shell
python -m unittest discover
```

增加新功能、修补漏洞后请在`tests`目录下增加或修改相应测试。在所有测试通过后提交Pull Request。
