import{_ as V,e as y,f as K,E as g,c as k,a as n,w as r,j as M,r as l,o as L,b as m,t as b,i as N,d as I,u as P,l as T}from"./index-BCFhymPB.js";import{m as O}from"./github-markdown-BOpQ1pHb.js";import{a as w}from"./axios-DXsv3KKR.js";const $={class:"submit"},D={class:"header"},H={key:0,class:"problem-info"},j=["innerHTML"],G="https://api.github.com",Y="xqy2006",q="Serverless-OJ",z={__name:"Submit",setup(F){const v=M(),S=P(),c=y(null),A=y(""),i=y({language:"cpp",code:""}),E=y(!1);K(async()=>{try{const e=await w.get(`/problems/${v.params.id}/problem.json`);c.value=e.data;const t=await w.get(`/problems/${v.params.id}/README.md`);A.value=O(t.data)}catch(e){console.error("Failed to load problem:",e),g.error("加载题目失败")}});async function R(e){const s=await(await fetch("/public_key.pem")).text(),u=await crypto.subtle.importKey("spki",U(s),{name:"RSA-OAEP",hash:"SHA-256"},!0,["encrypt"]),o=await crypto.subtle.generateKey({name:"AES-CBC",length:256},!0,["encrypt"]),p=crypto.getRandomValues(new Uint8Array(16)),f=await crypto.subtle.exportKey("raw",o),d=await crypto.subtle.encrypt({name:"RSA-OAEP"},u,f),h=new TextEncoder().encode(e),_=await crypto.subtle.encrypt({name:"AES-CBC",iv:p},o,h),a=new Uint8Array(d.byteLength+p.byteLength+_.byteLength);return a.set(new Uint8Array(d),0),a.set(p,d.byteLength),a.set(new Uint8Array(_),d.byteLength+p.byteLength),btoa(String.fromCharCode(...a))}function U(e){const t=e.replace("-----BEGIN PUBLIC KEY-----","").replace("-----END PUBLIC KEY-----","").replace(/\s/g,""),s=atob(t),u=new Uint8Array(s.length);for(let o=0;o<s.length;o++)u[o]=s.charCodeAt(o);return u.buffer}async function x(e,t){const s=localStorage.getItem("github_token");if(!s)throw new Error("No GitHub token found");return(await w.post(`${G}/repos/${Y}/${q}/issues`,{title:e,body:t},{headers:{Authorization:`token ${s}`,Accept:"application/vnd.github.v3+json"}})).data}const B=async()=>{E.value=!0;try{const e=await R(T().login+`
`+i.value.code);await x(c.value.title+"评测",e),g.success("提交成功"),setTimeout(()=>{S.push("/status")},3e3)}catch{g.error("提交失败")}};return(e,t)=>{const s=l("el-option"),u=l("el-select"),o=l("el-form-item"),p=l("el-input"),f=l("el-button"),d=l("el-form"),C=l("el-card"),h=l("el-col"),_=l("el-row");return L(),k("div",$,[n(_,{justify:"center"},{default:r(()=>[n(h,{span:20},{default:r(()=>[n(C,null,{header:r(()=>{var a;return[m("div",D,[m("h2",null,b((a=c.value)==null?void 0:a.title),1)])]}),default:r(()=>[c.value?(L(),k("div",H,[m("h5",null,"供题人："+b(c.value.author),1),m("h5",null,"内存限制："+b(c.value.memoryLimit)+" MB，时间限制："+b(c.value.timeLimit)+" ms",1),m("div",{class:"markdown-body",innerHTML:A.value},null,8,j)])):N("",!0),n(d,{model:i.value,class:"submit-form"},{default:r(()=>[n(o,{label:"编程语言"},{default:r(()=>[n(u,{modelValue:i.value.language,"onUpdate:modelValue":t[0]||(t[0]=a=>i.value.language=a),placeholder:"选择编程语言"},{default:r(()=>[n(s,{label:"C++",value:"cpp"})]),_:1},8,["modelValue"])]),_:1}),n(o,{label:"代码"},{default:r(()=>[n(p,{modelValue:i.value.code,"onUpdate:modelValue":t[1]||(t[1]=a=>i.value.code=a),type:"textarea",rows:15,placeholder:"在此输入你的代码"},null,8,["modelValue"])]),_:1}),n(o,null,{default:r(()=>[n(f,{type:"primary",disabled:E.value,onClick:B},{default:r(()=>t[2]||(t[2]=[I(" 提交代码 ")])),_:1},8,["disabled"])]),_:1})]),_:1},8,["model"])]),_:1})]),_:1})]),_:1})])}}},X=V(z,[["__scopeId","data-v-931e156d"]]);export{X as default};
