# coding:utf-8
from flask import render_template, abort, request, session, redirect, url_for, current_app, flash, make_response
from datetime import datetime
from app.email import send_email
from . import main
from .forms import NameForm, PostCommentForm, LiuyanCommentForm, EditProfileForm, EditProfileAdminForm, PostForm, \
    LiuyanForm, HeadtitleForm
import os
from .. import db
from ..models import User, Role, Post, Liuyan, Fenlei, Follow, PostComment, LiuyanComment, HeadTitle
from ..decorators import admin_required, permission_required
from ..models import Permission, allowed_file
from flask_login import login_required, current_user, logout_user, login_user
from werkzeug.utils import secure_filename
import shutil
from ..auth.forms import LoginForm


# 主页
@main.route('/', methods=['GET', 'POST'])
def index():
    # return render_template('modellogin.html', form=form, known=session.get('known', False))
    fenleis = True
    tujianposts = Post.query.order_by(Post.tuijiantime.desc()).limit(4).all()
    liuyans = Liuyan.query.order_by(Liuyan.timestamp.desc()).limit(4).all()
    rejipost = Post.query.order_by(Post.postrejicount.desc()).limit(4).all()
    repingpost = Post.query.order_by(Post.postcommentcount.desc()).limit(4).all()
    pythonposts = len(Post.query.filter_by(leibie='python').all())
    shujukuposts = len(Post.query.filter_by(leibie='shujuku').all())
    pacongposts = len(Post.query.filter_by(leibie='pacong').all())
    flaskposts = len(Post.query.filter_by(leibie='flask').all())
    weifenleiposts = len(Post.query.filter_by(leibie='weifenlei').all())
    titles = HeadTitle.query.order_by(HeadTitle.timestamp.desc()).limit(3)
    print titles
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', titles=titles, fenleis=fenleis, tuijianposts=tujianposts, liuyans=liuyans,
                           rejipost=rejipost,
                           repingpost=repingpost, pythonposts=pythonposts, shujukuposts=shujukuposts,
                           pacongposts=pacongposts,
                           flaskposts=flaskposts, weifenleiposts=weifenleiposts, form=form, posts=posts,
                           pagination=pagination, current_time=datetime.utcnow())


# 自定义头像
@main.route('/user/<username>/upload_file', methods=['GET', 'POST'])
@login_required
def upload_file(username):
    user = User.query.filter_by(username=username).first_or_404()
    isExists = os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], user.username))
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            try:
                os.mkdir(os.path.join(current_app.config['UPLOAD_FOLDER'], username))
            except:
                shutil.rmtree(os.path.join(current_app.config['UPLOAD_FOLDER'], username))
                os.mkdir(os.path.join(current_app.config['UPLOAD_FOLDER'], username))
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], os.path.join(username, filename)))
            filelist = os.listdir(os.path.join(current_app.config['UPLOAD_FOLDER'], username))
            i = 1
            for item in filelist:
                if item.endswith('.jpg'):
                    src = os.path.join(os.path.abspath(os.path.join(current_app.config['UPLOAD_FOLDER'], username)),
                                       item)
                    dst = os.path.join(os.path.abspath(os.path.join(current_app.config['UPLOAD_FOLDER'], username)),
                                       str(i) + '.jpg')
                    try:
                        os.rename(src, dst)
                    except:
                        pass
            flash('头像设置成功,请刷新试试')
            return redirect(url_for('.user', username=username))
        flash('头像定义失败')
        return redirect(url_for('.user', username=username))
    return ''''' 
    <!DOCTYPE html> 
    <title>Change new icon</title> 
    <h1>Upload new </h1> 
    <p>请把文件名命名为1.jpg,否则无法显示头像<p>
    <form action = "" method = "post" enctype=multipart/form-data> 
        <input type = "file" name = file> 
        <input type = "submit" value = Upload> 
    </form> 
    '''


# 推荐
@main.route('/tuijian/add', methods=['GET', 'POST'])
@login_required
@admin_required
def tuijian():
    id = request.args.get("id", '')
    post = Post.query.get_or_404(int(id))
    post.tuijian = post.tuijian + 1
    post.tuijiantime = datetime.utcnow()
    db.session.add(post)
    import json
    return json.dumps(dict(ok=1))




# 管理员主页
@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "For administrators!"


# 协管员主页
@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return "For comment moderators!"


# 用户个人资料主页
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    isExists = os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], user.username))
    page = request.args.get('page', 1, type=int)
    pagination = user.liuyans.order_by(Liuyan.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_LIUYANS_PER_PAGE'],
        error_out=False)
    liuyans = pagination.items
    return render_template('user.html', a=isExists, user=user, liuyans=liuyans,
                           pagination=pagination)


# 编辑个人资料普通用户
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('你的个人资料已经编辑完成')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


# 编辑个人资料管理员
@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    # 在这个视图函数中，用户由 id 指定，因此可使用 Flask-SQLAlchemy 提供的
    # get_or_404()函数，如果提供的 id不正确，则会返回 404 错误。
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('个人资料更新完成')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


# 留言板
@main.route('/liuyan', methods=['GET', 'POST'])
def liuyan():
    zuoze = User.query.filter_by(username='vip').first()
    all = Post.query.all()
    b = len(all)
    pythonposts = len(Post.query.filter_by(leibie='python').all())
    shujukuposts = len(Post.query.filter_by(leibie='shujuku').all())
    pacongposts = len(Post.query.filter_by(leibie='pacong').all())
    flaskposts = len(Post.query.filter_by(leibie='flask').all())
    weifenleiposts = len(Post.query.filter_by(leibie='weifenlei').all())

    form = LiuyanForm()
    if current_user.can(Permission.COMMENT) and \
            form.validate_on_submit():
        liuyan = Liuyan(body=form.body.data,
                        author=current_user._get_current_object())
        db.session.add(liuyan)
        return redirect(url_for('.liuyan'))
    # liuyans = Liuyans.query.order_by(Liuyans.timestamp.desc()).all()
    # return render_template('liuyan.html',form=form,liuyans=liuyans)
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_liuyans
    else:
        query = Liuyan.query
    pagination = query.order_by(Liuyan.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_LIUYANS_PER_PAGE'],
        error_out=False)
    liuyans = pagination.items
    return render_template('liuyan.html', zuoze=zuoze, b=b, pythonposts=pythonposts, shujukuposts=shujukuposts,
                           pacongposts=pacongposts,
                           flaskposts=flaskposts, weifenleiposts=weifenleiposts, user=user, form=form, liuyans=liuyans,
                           pagination=pagination, show_followed=show_followed)


@main.route('/liuyan/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.liuyan')))
    resp.set_cookie('show_followed', '', max_age=30 * 24 * 60 * 60)
    return resp


# 做了一个all 和 follow 的跟随效果 用true来控制
@main.route('/liuyan/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.liuyan')))
    resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)
    return resp


# 编辑文章专属网页
@main.route('/posts', methods=['GET', 'POST'])
@login_required
@admin_required
def posts():
    form = PostForm()
    if current_user.can(Permission.COMMENT) and \
            form.validate_on_submit():
        post = Post(body=form.body.data,
                    title=form.title.data,
                    leibie=form.leibie.data,
                    # fenlei=Fenlei.query.get(form.fenlei.data),
                    # fenlei = Fenlei.query.get(form.fenlei.data),
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.posts'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('posts.html', form=form, posts=posts)


# 分类
@main.route('/posts/<fenlei>', methods=['GET', 'POST'])
def postleibie(fenlei):
    liuyans = Liuyan.query.order_by(Liuyan.timestamp.desc()).limit(4).all()
    rejipost = Post.query.order_by(Post.postrejicount.desc()).limit(4).all()
    repingpost = Post.query.order_by(Post.postcommentcount.desc()).limit(4).all()
    pythonposts = len(Post.query.filter_by(leibie='python').all())
    shujukuposts = len(Post.query.filter_by(leibie='shujuku').all())
    pacongposts = len(Post.query.filter_by(leibie='pacong').all())
    flaskposts = len(Post.query.filter_by(leibie='flask').all())
    weifenleiposts = len(Post.query.filter_by(leibie='weifenlei').all())
    a = len(Post.query.filter_by(leibie=fenlei).all())
    posts = Post.query.filter_by(leibie=fenlei).all()
    posts.reverse()
    return render_template('python.html', fenleis=fenlei, liuyans=liuyans, rejipost=rejipost, repingpost=repingpost,
                           pythonposts=pythonposts, shujukuposts=shujukuposts, pacongposts=pacongposts,
                           flaskposts=flaskposts, weifenleiposts=weifenleiposts, posts=posts, a=a,
                           current_time=datetime.utcnow())


# 文章id
@main.route('/posts/<int:id>', methods=['GET', 'POST'])
def post(id):
    pythonposts = len(Post.query.filter_by(leibie='python').all())
    shujukuposts = len(Post.query.filter_by(leibie='shujuku').all())
    pacongposts = len(Post.query.filter_by(leibie='pacong').all())
    flaskposts = len(Post.query.filter_by(leibie='flask').all())
    weifenleiposts = len(Post.query.filter_by(leibie='weifenlei').all())

    zuoze = User.query.filter_by(username='vip').first()
    post = Post.query.get_or_404(id)
    userone = os.path.join('{}'.format(post.author.username), '{}'.format(id))
    path = os.path.join(current_app.config['UPLOAD_FOLDER_POSTS'], userone)
    isExists = os.path.exists(path)
    if isExists:
        images = len(os.listdir(path))
    else:
        images = False
    fenleis = post.leibie
    post.postrejicount = post.postrejicount + 1
    db.session.add(post)
    allposts = Post.query.all()
    b = len(allposts)
    form = PostCommentForm()
    if form.validate_on_submit():
        comment = PostComment(body=form.body.data,
                              post=post, author=current_user._get_current_object())
        post.postcommentcount = post.postcommentcount + 1

        db.session.add(comment)
        db.session.add(post)
        flash('你的评论已经发表')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.postcomments.count() - 1) // \
               current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.postcomments.order_by(PostComment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', zuoze=zuoze, filelist=images, b=b, isExists=isExists, fenleis=fenleis,
                           post=post, pythonposts=pythonposts, shujukuposts=shujukuposts,
                           pacongposts=pacongposts,
                           flaskposts=flaskposts, weifenleiposts=weifenleiposts, posts=[post], form=form,
                           comments=comments, pagination=pagination, current_time=datetime.utcnow())


# 编辑文章id
@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        db.session.add(post)
        flash('这篇文章已经更新')
        return redirect(url_for('.post', id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    return render_template('edit_post.html', id=post.id, form=form, current_time=datetime.utcnow())


# 定义首页标题
@main.route('/index/headtitle', methods=['GET', 'POST'])
@login_required
@admin_required
def head_title():
    form = HeadtitleForm()
    if form.validate_on_submit():
        head = HeadTitle(title=form.title.data,
                         body=form.body.data)
        db.session.add(head)
        return redirect(url_for('.index'))
    return render_template('headtitle.html', form=form)


# 删除文章图片
@main.route('/edit/<int:id>/delete', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_image(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    userone = os.path.join('{}'.format(post.author.username), '{}'.format(id))
    path = os.path.join(current_app.config['UPLOAD_FOLDER_POSTS'], userone)
    isExists = os.path.exists(path)
    if isExists:
        shutil.rmtree(path)
        flash('图片已经删除')
    else:
        flash('没有图片可以删除')
    return redirect(url_for('.edit', id=id))


# 删除首页图片
@main.route('/delete_headiamge', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_head_image():
    path = current_app.config['UPLOAD_FOLDER_POSTS']
    isExists = os.path.exists(path)
    if isExists:
        shutil.rmtree(path)
        flash('图片已经删除')
    else:
        flash('没有图片可以删除')
    return redirect(url_for('.index'))


# 上传首页封面图片
@main.route('/headimage', methods=['GET', 'POST'])
@login_required
@admin_required
def upload_head_image():
    path = current_app.config['UPLOAD_FOLDER_HEADIMAGE']
    isExists = os.path.exists(path)
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            try:
                os.makedirs(path)
            except:
                pass
            filename = secure_filename(file.filename)
            file.save(os.path.join(path, filename))
            filelist = os.listdir(path)
            i = 0
            for item in filelist:
                src = os.path.join(os.path.abspath(path), item)
                dst = os.path.join(os.path.abspath(path), str(i) + '.jpg')
                try:
                    os.rename(src, dst)
                    i += 1
                except:
                    pass
            flash('图片已经上传成功,请刷新试试')
            return redirect(url_for('.index'))
        flash('图片上传失败，请重新试试')
        return redirect(url_for('.index'))
    return ''''' 
        <!DOCTYPE html> 
        <title>Change new icon</title> 
        <h1>Upload new </h1> 
        <p>请把文件名命名为1.jpg,否则无法显示头像<p>
        <form action = "" method = "post" enctype=multipart/form-data> 
            <input type = "file" name = file> 
            <input type = "submit" value = Upload> 
        </form> 
        '''


# 上传文章图片
@main.route('/edit/<int:id>/upload', methods=['GET', 'POST'])
@login_required
@admin_required
def upload_image(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    # a = os.path.join(post.author,id)
    userone = os.path.join('{}'.format(current_user.username), '{}'.format(id))
    path = os.path.join(current_app.config['UPLOAD_FOLDER_POSTS'], userone)
    isExists = os.path.exists(path)
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            try:
                os.makedirs(path)
            except:
                pass
            filename = secure_filename(file.filename)
            file.save(os.path.join(path, filename))
            filelist = os.listdir(path)
            i = 0
            for item in filelist:
                src = os.path.join(os.path.abspath(path), item)
                dst = os.path.join(os.path.abspath(path), str(i) + '.jpg')
                try:
                    os.rename(src, dst)
                    i += 1
                except:
                    pass
            flash('图片已经上传成功,请刷新试试')
            return redirect(url_for('.edit', id=id))
        flash('图片上传失败，请重新试试')
        return redirect(url_for('.edit', id=id))
    return ''''' 
        <!DOCTYPE html> 
        <title>Change new icon</title> 
        <h1>Upload new </h1> 
        <p>请把文件名命名为1.jpg,否则无法显示头像<p>
        <form action = "" method = "post" enctype=multipart/form-data> 
            <input type = "file" name = file> 
            <input type = "submit" value = Upload> 
        </form> 
        '''


# 协管员 管理评论的路由
@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = PostComment.query.order_by(PostComment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)


# 评论的路由的显示
@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = PostComment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))


# 评论屏蔽
@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = PostComment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))


# 关注
@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户错误')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('你已经关注了他')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash('你正在关注 {}'.format(username))
    return redirect(url_for('.user', username=username))


# 取消关注
@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户错误')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('你已经取消关注他')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash('你已经取消关注{}'.format(username))
    return redirect(url_for('.user', username=username))


# 粉丝
@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('无效用户.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="粉丝",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


# 关注的人
@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('无效用户')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', user=user, title='关注',
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)

# 显示所有博客文章或只显示所关注用户的文章
