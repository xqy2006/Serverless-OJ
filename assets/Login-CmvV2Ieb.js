import{_ as b,e as _,f as C,c as p,g,w as a,a as l,b as h,s as R,h as B,E,r as s,o as i,d as I,i as N,u as T,j as x}from"./index-xhqn28Dn.js";const L={class:"login-container"},j={key:1,class:"loading-container"},m="Iv23li6mS71Nl5c3wBwB",U={__name:"Login",setup(z){const w=window.location.origin+"/#/login";T();const f=x(),r=_(!1),u=_(""),k=()=>{const o=`https://github.com/login/oauth/authorize?client_id=${m}&redirect_uri=${w}`;window.location.href=o},y=async o=>{try{r.value=!0;const t=await(await fetch("https://github-oa.xuqinyang.us.kg/",{method:"POST",headers:{Accept:"application/json","Content-Type":"application/json"},body:JSON.stringify({client_id:m,code:o})})).json();if(t.access_token){R(t.access_token);const n=await(await fetch("https://api.github.com/user",{headers:{Authorization:`token ${t.access_token}`}})).json();B({id:n.id,login:n.login,avatar_url:n.avatar_url});const c=f.query.redirect||"/";window.location.href=window.location.origin+"/#"+c}else throw new Error("Failed to get access token")}catch(e){console.error("Login failed:",e),E.error("登录失败，请重试")}finally{r.value=!1}};return C(()=>{const e=new URLSearchParams(window.location.search).get("code");e&&(u.value=e,y(e))}),(o,e)=>{const t=s("i-ep-position"),d=s("el-icon"),n=s("el-button"),c=s("el-card"),v=s("el-spinner");return i(),p("div",L,[r.value?(i(),p("div",j,[l(v,{size:"large"}),e[2]||(e[2]=h("p",null,"正在登录中...",-1))])):(i(),g(c,{key:0,class:"login-card"},{header:a(()=>e[0]||(e[0]=[h("h2",null,"登录 GitHub",-1)])),default:a(()=>[u.value?N("",!0):(i(),g(n,{key:0,type:"primary",onClick:k,size:"large"},{default:a(()=>[l(d,null,{default:a(()=>[l(t)]),_:1}),e[1]||(e[1]=I(" 使用 GitHub 账号登录 "))]),_:1}))]),_:1}))])}}},S=b(U,[["__scopeId","data-v-e24e9a16"]]);export{S as default};
