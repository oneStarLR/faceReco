# 基于树莓派的人脸识别门禁系统

## 一、功能概述
&emsp;&emsp;该软件实现的是人脸识别门禁功能，通过树莓派作为终端处理，使用OpenCV来识别人脸，从而达到特定的人脸开门的目的。主要分为管理员登录、录入人脸、识别人脸三大功能，管理员输入用户名和密码可以登录进入管理界面，在管理界面中录入人脸，录入人脸主要是人脸检测、捕获人脸、训练人脸，最后通过人脸识别实现开门的功能。

## 二、开发工具
&emsp;&emsp;开发工具使用的是Python2.7作为开发语言，OpenCV3.4.0作为图像处理库，PyQt5作为界面显示工具，使用树莓派自带的Geany编辑器。

注：本来搭建OpenCV环境和PyQt5的时候是按照python3.5来的，开发到一半发现用的是python2.7的版本....不过最终效果还是出来了

## 三、运行环境
硬件：树莓派3B+

镜像系统：2019-04-08-raspbian-stretch-full.img

软件：python2.7+OpenCV3.4.0+PyQt5

HDMI显示屏：10.1寸、分辨率1280*800

## 四、用户手册
### 1、系统主界面
启动树莓派，就能看到主界面，如下：
![image](https://note.youdao.com/yws/api/personal/file/20242355ABB944ADBCD920197AF758B2?method=download&shareKey=589a6e92faf56f38e0edb05bddbd122b)
主界面是“欢迎使用人脸识别门禁系统”字样和普通用户、管理员两个功能按键，点击能进入相应的功能界面。

### 2、登录界面
点击主界面的管理员按键，进入管理员登录界面，输入响应的账号和密码点击登录即可进入管理员管理界面，默认初始账号为1，密码为1，点击返回能返回主界面。
![image](https://note.youdao.com/yws/api/personal/file/39359DDF68E348169723D6ACB9DCE06E?method=download&shareKey=f7cf265b18759eb12371f6b15e82443f)

### 3、人脸录入界面
![image](https://note.youdao.com/yws/api/personal/file/C884B31EB077466FA26A3CEBDFF4D3F6?method=download&shareKey=a18c84c8bab2651f018522bcce671d4c)

#### 3.1 人脸检测
在人脸录入界面中，左边是摄像头视屏采集界面，能够将视频图像显示到界面中，并对人脸进行检测，将图像中所有的人脸检测出来，并用矩形框框出。

#### 3.2 人脸捕获和训练
在人脸录入界面中，右边是管理员需要操作的部分，待录入人员对准摄像头，管理员输入相应的ID，点击开始录入，等待进度条加载完毕即完成人脸录入，在进度条加载的过程中，完成了人脸录入和训练人脸的两个过程，人脸捕获时会自动在程序目录下创建文件夹保存60张人脸图片，训练人脸会读取捕获的人脸图像进行识别训练，并将训练数据保存在程序目录下的文件中。

### 4、人脸识别开门功能
点击返回回到主界面，点击普通用户，进入普通用户界面，待识别人员对准摄像头，能将录入的人员识别出，并显示ID，在右边会有相关提示信息，身份认证成功能控制舵机开门。
![image](https://note.youdao.com/yws/api/personal/file/14ABB237F7124661992BB3045971547B?method=download&shareKey=c56967a8a4868a6bde4aff68ec216b66)

在CSDN上有比较详细的解说，可以参考参考：https://blog.csdn.net/One_L_Star/article/details/99837868
