import{_ as j,e as d,f as F,k as L,c as M,a as t,w as s,r as o,o as T,b,d as V,t as z,u as $}from"./index-DCu4WCpA.js";import{a as P}from"./axios-DXsv3KKR.js";const q={class:"problems"},E={class:"header"},Q={class:"filters"},A={class:"pagination"},G={__name:"Problems",setup(H){$();const v=d(""),f=d(""),n=d(1),u=d(10),g=d(0),x=d([]),h=async(l=1,e=10)=>{try{const i=(await P.get("/problems/list.txt")).data.split(`
`).filter(c=>c.trim());g.value=i.length;const p=(l-1)*e,m=Math.min(p+e,g.value),y=await Promise.all(i.slice(p,m).map(async(c,_)=>{const w=p+_+1;return(await P.get(`/problems/${w}/problem.json`)).data}));x.value=y.sort((c,_)=>_.id-c.id)}catch(r){console.error("Failed to load problems:",r)}};F(()=>{h(n.value,u.value)});const S=L(()=>{let l=x.value;if(v.value){const e=v.value.toLowerCase();l=l.filter(r=>r.title.toLowerCase().includes(e)||r.id.toString().includes(e))}return f.value&&(l=l.filter(e=>e.difficulty===f.value)),l}),k=l=>({easy:"success",medium:"warning",hard:"danger"})[l],I=()=>{n.value=1},D=()=>{n.value=1},N=l=>{u.value=l,h(n.value,u.value)},U=l=>{n.value=l,h(n.value,u.value)};return(l,e)=>{const r=o("el-input"),i=o("el-option"),p=o("el-select"),m=o("el-table-column"),y=o("router-link"),c=o("el-tag"),_=o("el-table"),w=o("el-pagination"),C=o("el-card"),B=o("el-col"),R=o("el-row");return T(),M("div",q,[t(R,{justify:"center"},{default:s(()=>[t(B,{xs:24,sm:22,md:20},{default:s(()=>[t(C,{class:"problem-card"},{header:s(()=>[b("div",E,[e[4]||(e[4]=b("h2",null,"题目列表",-1)),b("div",Q,[t(r,{modelValue:v.value,"onUpdate:modelValue":e[0]||(e[0]=a=>v.value=a),placeholder:"搜索题目或ID","prefix-icon":"Search",onInput:I,class:"filter-item"},null,8,["modelValue"]),t(p,{modelValue:f.value,"onUpdate:modelValue":e[1]||(e[1]=a=>f.value=a),placeholder:"难度",onChange:D,class:"filter-item"},{default:s(()=>[t(i,{label:"全部",value:""}),t(i,{label:"简单",value:"easy"}),t(i,{label:"中等",value:"medium"}),t(i,{label:"困难",value:"hard"})]),_:1},8,["modelValue"])])])]),default:s(()=>[t(_,{data:S.value,style:{width:"100%"},class:"responsive-table"},{default:s(()=>[t(m,{prop:"id",label:"编号",width:"80",sortable:"desc"}),t(m,{prop:"title",label:"标题","min-width":"120"},{default:s(a=>[t(y,{to:`/submit/${a.row.id}`},{default:s(()=>[V(z(a.row.title),1)]),_:2},1032,["to"])]),_:1}),t(m,{prop:"difficulty",label:"难度",width:"100"},{default:s(a=>[t(c,{type:k(a.row.difficulty)},{default:s(()=>[V(z(a.row.difficulty),1)]),_:2},1032,["type"])]),_:1})]),_:1},8,["data"]),b("div",A,[t(w,{"current-page":n.value,"onUpdate:currentPage":e[2]||(e[2]=a=>n.value=a),"page-size":u.value,"onUpdate:pageSize":e[3]||(e[3]=a=>u.value=a),total:g.value,"page-sizes":[10,20,50,100],layout:"total, sizes, prev, pager, next",onSizeChange:N,onCurrentChange:U,class:"responsive-pagination"},null,8,["current-page","page-size","total"])])]),_:1})]),_:1})]),_:1})])}}},O=j(G,[["__scopeId","data-v-fc8b552e"]]);export{O as default};