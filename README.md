#flask+mysql+bootstrap   
博客支持 自定义头像，文章带图等基本功能  

如果使用可能需要先设置 环境变量  由于注册等操作需要邮件验证  所以需要设置系统变量  
Mac OS X 中使用 bash，那么可以按照下面的方式设定这两个变量：
(venv) $ export MAIL_USERNAME=<Gmail username>
(venv) $ export MAIL_PASSWORD=<Gmail password>
微软 Windows 用户可按照下面的方式设定环境变量：
(venv) $ set MAIL_USERNAME=xxxxxxx@163.com
(venv) $ set MAIL_PASSWORD=xxxx   这里密码注意了 需要去网易邮箱设置 授权码  然后这里填写授权码  具体可以百度网易授权码
(venv) $ set DFK_ADMIN=<Gmail username>  这是 别人注册了 就给你发送一个邮件提示  
  我用的163.eamil    
  由于一些问题  网站需要一些初始值 例如 首页的的title  所以我提供的直用版中 有数据库文件   如果没有这些初始值 可能报错，所以可以根据自己修改   
  数据库文件 包含一个 管理员用户  用户名：vip  邮箱：xxxxxxx@163.com 密码：1 登录 可以用这个登录 然后 去数据库中修改就可以  
  #由于我是跟着flask web 这本书做的 所以登录都是普通表单  
  然后发现模态登录挺好的  就做了一个模态登录  但是不像改太多数据  
  因此 只有登录是模态的  其他的 都没有做更改  
 
  
  
