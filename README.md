# 写在最前面
>> 如果身体出现问题，一定要手动上报。但如果身体没事，又想我一样懒得每天做一遍重复工作，跑脚本就完事了


# 运行步骤
0. 安装python3.x

1. 在项目文件夹里新建虚拟环境并进入

   ```shell
   python3 -m venv venv
   source venv/bin/activate
   ```

2. 安装依赖库requests和requests-html

   ```shell
   pip3 install requests requests-html
   ```

3. 修改 config.py文件，改为自己的学号密码

4. 运行 run.py，即可将昨天上报情况重复填入

   ```shell
   python3 run.py
   ```

5. 建议有条件的同学配置在服务器上，每天跑一次即可（或者可以添加为电脑开机自动运行之类的）
