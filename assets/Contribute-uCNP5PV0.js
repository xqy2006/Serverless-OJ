import{m as d}from"./github-markdown-BOpQ1pHb.js";import{_,e as i,f as p,c as u,a as o,w as e,r as t,o as m,b as n}from"./index-BPkb2VXz.js";const f={class:"contribute"},b=["innerHTML"],h={__name:"Contribute",setup(k){const s=i("");return p(async()=>{s.value=d(`#### 准备材料

- 题目描述、时长限制、内存限制
- 多组输入（后缀为in）、输出（后缀为out）

#### 操作步骤

1. 前往[代码仓库](https://github.com/xqy2006/Serverless-OJ/)进行fork，将fork的仓库clone到本地

2. 在problems文件夹下新建\`题目名称\`文件夹（无需修改list.txt，会自动更新）

3. 在\`题目名称\`文件夹下放入输入、输出文件，并编写problem.json（格式参考已有题目）
4. 在仓库根目录下运行\`python encrypt.py ./problems/题目名称\`，会生成in.enc和out.enc文件
5. 删除\`题目名称\`文件夹下的in文件和out文件
6. \`git add .\` \`git commit\` \`git push\`将本地更改应用到fork仓库中
7. 发起PR，等待审核`)}),(v,r)=>{const a=t("el-card"),c=t("el-col"),l=t("el-row");return m(),u("div",f,[o(l,{justify:"center"},{default:e(()=>[o(c,{span:20},{default:e(()=>[o(a,null,{header:e(()=>r[0]||(r[0]=[n("div",{class:"header"},[n("h2",null,"贡献题目")],-1)])),default:e(()=>[n("div",{class:"markdown-body",innerHTML:s.value},null,8,b)]),_:1})]),_:1})]),_:1})])}}},x=_(h,[["__scopeId","data-v-584426d8"]]);export{x as default};
