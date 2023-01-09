# 微博备份

备份新浪微博指定用户的全部微博，文本数据保存到redis数据库文件，图片文件保存到仓库的文件夹下，并以markdown格式输出到json。

## 安装

```
git clone https://github.com/shaoyaoqian/weibo-shaoyaoqian.git
cd weibo-shaoyaoqian
pip install requirements.txt
```

## 使用
0. 删除 `main` 分支中的 `dump.rdb` 文件，创建 `output` 分支
1. 在 `.github/workflows/main.yml` 中设置微博ID `WEIBO_USER`
2. 在 `weibospider/cookie.txt` 中设置 cookies
3. 将代码 push 到 GitHub 仓库，开启 GitHub Action

### 可选设置
1. 默认只下载最新的25条微博，如需下载所有微博，注释 `weibospider/settings.py` 代码中的 `DEPTH_LIMIT = 1`
2. 设置 vercel 反向代理加速图片文件加载，修改 `output/convert.py` 中的代码 `pic_cdn_url_base` 和 `pic_original_cdn_url_base` 变量
3. 将微博内容添加到博客中

### 效果展示
(随便找的微博账号)
<img width="300" alt="image" src="https://githubimages.pengfeima.cn/images/202301052051494.png">
<img width="300" alt="image" src="https://user-images.githubusercontent.com/115222128/210935526-22d1359b-8113-4482-a228-44023cf3ee62.png">
<img width="300" alt="image" src="https://user-images.githubusercontent.com/115222128/210935575-3ca51d75-d19f-495b-af1c-2f38bf301154.png">
<img width="300" alt="image" src="https://user-images.githubusercontent.com/115222128/210935601-f7b21ea3-800e-4533-96b4-241773997f43.png">
<img width="300" alt="image" src="https://user-images.githubusercontent.com/115222128/210935663-b0a2b4e8-17b8-4bed-a091-d2878ef6259d.png">

#### 移动端



![4721673065737_.pic](https://githubimages.pengfeima.cn/images/202301071257978.jpg)

![4681673065735_.pic](https://githubimages.pengfeima.cn/images/202301071258295.jpg)

![4701673065736_.pic](https://githubimages.pengfeima.cn/images/202301071258553.jpg)

![4711673065737_.pic](https://githubimages.pengfeima.cn/images/202301071257199.jpg)









## Contributing

PRs accepted.

## License

MIT

## 代码及作者

[WeiboSpider](https://github.com/shaoyaoqian/WeiboSpider)

[shaoyaoqian](https://github.com/shaoyaoqian)

[readme模板](https://github.com/felixchen0707/standard-readme/blob/master/example-readmes/minimal-readme.md)

## TODO

1. 爬取视频
