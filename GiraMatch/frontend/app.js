/* GiraMatch — núcleo compartilhado do front-end (API, sessão, layout, utilitários, modo demonstração) */
'use strict';

const GM = {};
/* Endereço da API hospedada. VAZIO ('') = site sem servidor: o login com as contas de demonstração funciona sozinho
   (modo demonstração, dados fictícios). Quando a API estiver publicada, coloque a URL real aqui (ex.: 'https://seu-servico.onrender.com').
   Em localhost usa a API local e, se ela estiver desligada, cai no modo demonstração. */
const API_PRODUCAO = '';
const EM_LOCAL = ['localhost', '127.0.0.1', ''].includes(location.hostname);
const API_PADRAO = EM_LOCAL ? 'http://127.0.0.1:8000' : API_PRODUCAO;
GM.API = (() => { try { return localStorage.getItem('gm_api') || API_PADRAO; } catch { return API_PADRAO; } })();

/* ---------- utilitários ---------- */
const MESES = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];
const NAT = { contratacao: 'Contratação', capacitacao: 'Capacitação', outra: 'Outra necessidade' };
const TIPO = { material: 'Material', servico: 'Serviço', capacitacao: 'Capacitação', outro: 'Outro' };

const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
GM.esc = esc;
GM.brl = (v) => (v == null ? null : Number(v).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }));
GM.num = (v) => Number(v).toLocaleString('pt-BR', { maximumFractionDigits: 1 });
GM.pct = (v) => (v == null ? '—' : (v * 100).toFixed(1).replace('.', ',') + '%');
GM.qtd = (d) => `${GM.num(d.quantidade)} ${esc(d.unidade || '')}`;
GM.mes = (d) => `${MESES[d.mes_previsto - 1]}/${d.ano}`;
GM.data = (iso) => {
  if (!iso) return '—';
  const [a, m, d] = String(iso).slice(0, 10).split('-');
  return d ? `${d}/${m}/${a}` : iso;
};
GM.hoje = () => new Date().toISOString().slice(0, 10);
/* Prazo do contrato: até 60 dias = alerta; até 30 dias (ou vencido) = alerta crítico. */
GM.contrato = (iso) => {
  if (!iso) return null;
  const [a, m, d] = String(iso).slice(0, 10).split('-').map(Number);
  const [ha, hm, hd] = GM.hoje().split('-').map(Number);
  const dias = Math.round((Date.UTC(a, m - 1, d) - Date.UTC(ha, hm - 1, hd)) / 864e5);
  if (dias < 0) return { dias, nivel: 'critico', cls: 'a-bad', badge: 'b-bad', rot: 'Contrato vencido', texto: `O contrato venceu há ${-dias} dia(s) (${GM.data(iso)}).` };
  if (dias <= 30) return { dias, nivel: 'critico', cls: 'a-bad', badge: 'b-bad', rot: 'Alerta crítico', texto: dias === 0 ? 'O contrato vence hoje.' : `Faltam apenas ${dias} dia(s) para o fim do contrato (${GM.data(iso)}).` };
  if (dias <= 60) return { dias, nivel: 'alerta', cls: 'a-warn', badge: 'b-warn', rot: 'Alerta', texto: `Faltam ${dias} dias para o fim do contrato (${GM.data(iso)}).` };
  return { dias, nivel: 'ok', cls: 'a-ok', badge: 'b-ok', rot: 'No prazo', texto: `Contrato vigente até ${GM.data(iso)} (${dias} dias).` };
};
GM.param = (nome) => new URLSearchParams(location.search).get(nome);

const ICONES = {
  home: '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
  lista: '<line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/>',
  plus: '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/>',
  match: '<circle cx="9" cy="12" r="6"/><circle cx="15" cy="12" r="6"/>',
  mail: '<path d="M4 4h16a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z"/><polyline points="22,6 12,13 2,6"/>',
  users: '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
  alerta: '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
  pulso: '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
  sair: '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>',
};
const ico = (n) => `<svg viewBox="0 0 24 24" aria-hidden="true">${ICONES[n]}</svg>`;

GM.marca = `<svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="18" cy="24" r="13" fill="#1f5f9e" opacity=".95"/><circle cx="30" cy="24" r="13" fill="#e8a50e" opacity=".92"/><path d="M24 14.2a13 13 0 0 1 0 19.6 13 13 0 0 1 0-19.6z" fill="#fff" opacity=".9"/></svg>`;

GM.toast = (msg, tipo = '') => {
  let box = document.querySelector('.toasts');
  if (!box) { box = document.createElement('div'); box.className = 'toasts'; box.setAttribute('role', 'status'); document.body.appendChild(box); }
  const t = document.createElement('div');
  t.className = 'toast ' + tipo;
  t.textContent = msg;
  box.appendChild(t);
  setTimeout(() => t.remove(), 4500);
};

GM.confirmar = (titulo, texto, rotulo = 'Confirmar', perigo = false) => new Promise((resolve) => {
  const d = document.createElement('dialog');
  d.innerHTML = `<h2>${esc(titulo)}</h2><p class="muted" style="margin-top:8px">${esc(texto)}</p>
    <div class="row"><button class="btn" value="no">Cancelar</button><button class="btn ${perigo ? 'btn-danger' : 'btn-primary'}" value="yes">${esc(rotulo)}</button></div>`;
  document.body.appendChild(d);
  d.addEventListener('click', (e) => { const v = e.target.value; if (v) d.close(v); });
  d.addEventListener('close', () => { resolve(d.returnValue === 'yes'); d.remove(); });
  d.showModal();
});

GM.armazenar = {
  ler(k, padrao) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : padrao; } catch { return padrao; } },
  gravar(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* ignora */ } },
};

/* ---------- sessão e API ---------- */
GM.sessao = () => { try { return JSON.parse(sessionStorage.getItem('gm_sessao')); } catch { return null; } };
GM.salvarSessao = (s) => sessionStorage.setItem('gm_sessao', JSON.stringify(s));

GM.api = async (metodo, caminho, corpo, tipo) => {
  const s = GM.sessao();
  if (s && s.demo) return Demo.chamar(metodo, caminho, corpo);
  const h = {};
  if (s && s.token) h.Authorization = 'Bearer ' + s.token;
  let body;
  if (corpo !== undefined) {
    if (typeof corpo === 'string') { body = corpo; h['Content-Type'] = tipo || 'text/csv'; }
    else { body = JSON.stringify(corpo); h['Content-Type'] = 'application/json'; }
  }
  let r;
  // Só o login tem limite de tempo: se o servidor não responde em 10 s, a tela cai no modo demonstração.
  const ctrl = caminho === '/api/auth/login' ? new AbortController() : null;
  const timer = ctrl ? setTimeout(() => ctrl.abort(), 10000) : null;
  try { r = await fetch(GM.API + caminho, { method: metodo, headers: h, body, signal: ctrl ? ctrl.signal : undefined }); }
  catch { throw Object.assign(new Error(`Não foi possível conectar à API (${GM.API}). Ela está rodando?`), { rede: true }); }
  if (timer) clearTimeout(timer);
  // Login: servidor inexistente (404) ou acordando/fora do ar (502, 503, 504) conta como "sem servidor" e cai no modo demonstração.
  if (caminho === '/api/auth/login' && [404, 502, 503, 504].includes(r.status)) {
    throw Object.assign(new Error(`Servidor indisponível (${GM.API}).`), { rede: true });
  }
  let dados = null;
  try { dados = await r.json(); } catch { /* sem corpo */ }
  if (r.status === 401 && s && caminho !== '/api/auth/login') {
    sessionStorage.removeItem('gm_sessao');
    location.href = 'index.html?expirou=1';
    throw new Error('Sessão expirada.');
  }
  if (!r.ok) throw Object.assign(new Error((dados && dados.erro) || `Erro ${r.status}`), { status: r.status });
  return dados;
};

GM.sair = async () => {
  try { await GM.api('POST', '/api/auth/logout'); } catch { /* ignora */ }
  sessionStorage.removeItem('gm_sessao');
  location.href = 'index.html';
};

/* ---------- moldura das páginas ---------- */
const NAV_GESTOR = [
  ['Visão geral', [['dashboard', 'dashboard.html', 'Painel', 'home'], ['minhas', 'minhas-demandas.html', 'Minhas demandas', 'lista'], ['nova', 'nova-demanda.html', 'Nova demanda', 'plus']]],
  ['Cooperação', [['matches', 'matches.html', 'Matches', 'match'], ['convites', 'convites.html', 'Convites', 'mail'], ['comite', 'comite.html', 'Comitês', 'users'], ['acomp', 'acompanhamento.html', 'Acompanhamento', 'pulso'], ['ocorr', 'ocorrencias.html', 'Ocorrências', 'alerta']]],
];
/* Perfil de fiscalização: só acompanha as iniciativas (somente leitura) e registra/gerencia ocorrências. */
const NAV_FISCAL = [
  ['Fiscalização', [['acomp', 'acompanhamento.html', 'Acompanhamento', 'pulso'], ['ocorr', 'ocorrencias.html', 'Ocorrências', 'alerta']]],
];

GM.pagina = async (ativa, titulo, render) => {
  const s = GM.sessao();
  if (!s) { location.href = 'index.html'; return; }
  const fiscal = !!(s.usuario && s.usuario.perfil === 'fiscal');
  if (fiscal && !['acomp', 'ocorr'].includes(ativa)) { location.href = 'acompanhamento.html'; return; }
  document.title = `${titulo} — GiraMatch`;
  const nav = (fiscal ? NAV_FISCAL : NAV_GESTOR).map(([sec, itens]) => `<div class="nav-sec">${sec}</div>` + itens.map(([k, href, rot, ic]) =>
    `<a href="${href}" class="${k === ativa ? 'ativo' : ''}" ${k === ativa ? 'aria-current="page"' : ''}>${ico(ic)}<span>${rot}</span>${k === 'convites' ? '<span class="badge-n hidden" id="nav-conv"></span>' : ''}</a>`).join('')).join('');
  document.getElementById('app').innerHTML = `
    <div class="layout">
      <aside class="side" id="side">
        <a class="logo-box" href="dashboard.html" aria-label="GiraMatch — painel"><img src="logo-giramatch-claro.png" alt="GiraMatch"></a>
        <nav class="nav" aria-label="Principal">${nav}</nav>
        <div class="side-foot"><small>Órgão</small><strong>${esc(s.orgao.sigla)}</strong><small>Usuário</small><span>${esc(s.usuario.nome)}</span>
          <button id="btn-sair" type="button">Sair</button></div>
      </aside>
      <div class="content">
        <header class="top"><button class="btn btn-sm burger" id="burger" aria-label="Abrir menu" type="button">☰</button>
          <h1>${esc(titulo)}</h1>${s.demo ? '<span class="demo-tag" title="Dados fictícios guardados só neste navegador">Modo demonstração</span>' : ''}
          <span class="right muted small">${esc(s.orgao.nome)}</span>
          <div class="sino-box"><button class="sino" id="sino" type="button" aria-label="Alertas de contrato" aria-expanded="false" aria-controls="sino-painel">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
            <span class="sino-n hidden" id="sino-n"></span></button>
            <div class="sino-painel hidden" id="sino-painel" role="region" aria-label="Alertas de contrato"></div></div></header>
        <main class="main" id="main"><div class="skeleton"></div><div class="skeleton"></div></div>
      </div>
    </div>`;
  document.getElementById('btn-sair').onclick = GM.sair;
  const side = document.getElementById('side');
  const burger = document.getElementById('burger');
  const fechar = () => { side.classList.remove('aberto'); burger.setAttribute('aria-expanded', 'false'); document.body.style.overflow = ''; };
  burger.setAttribute('aria-expanded', 'false');
  burger.onclick = () => { const a = side.classList.toggle('aberto'); burger.setAttribute('aria-expanded', String(a)); document.body.style.overflow = a ? 'hidden' : ''; };
  side.addEventListener('click', (e) => { if (e.target.closest('a')) fechar(); });
  document.addEventListener('click', (e) => { if (side.classList.contains('aberto') && !side.contains(e.target) && !e.target.closest('#burger')) fechar(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') fechar(); });
  const main = document.getElementById('main');
  try { await render(main, s); }
  catch (e) { main.innerHTML = `<div class="alert a-bad" role="alert"><div><strong>Algo deu errado.</strong><br>${esc(e.message)}</div></div>`; }
  GM.ligarSino();
  GM.atualizarSino();
  GM.atualizarBadgeConvites();
  GM.alertaPedidos();
  if (!GM._poll) GM._poll = setInterval(() => { if (!document.hidden) { GM.atualizarBadgeConvites(); GM.alertaPedidos(); GM.atualizarSino(); } }, 15000);
  document.addEventListener('visibilitychange', () => { if (!document.hidden) GM.alertaPedidos(); });
};

/* ---------- sininho: contratos a 60 dias do fim (alerta) ou 30 dias (crítico) ---------- */
GM.ligarSino = () => {
  const btn = document.getElementById('sino'), painel = document.getElementById('sino-painel');
  const fechar = () => { painel.classList.add('hidden'); btn.setAttribute('aria-expanded', 'false'); };
  btn.onclick = () => { const abrir = painel.classList.contains('hidden'); painel.classList.toggle('hidden', !abrir); btn.setAttribute('aria-expanded', String(abrir)); };
  document.addEventListener('click', (e) => { if (!e.target.closest('.sino-box')) fechar(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') fechar(); });
};
/* ---------- ocorrências da fiscalização ---------- */
GM.TIPOS_OC = { inconsistencia: 'Inconsistência', falha: 'Falha', falta_informacao: 'Falta de informação', intercorrencia: 'Intercorrência' };
GM.STATUS_OC = { aberta: ['Aberta', 'b-bad'], respondida: ['Respondida', 'b-warn'], resolvida: ['Resolvida', 'b-ok'] };
GM.GRAV_OC = { baixa: ['Baixa', 'b-pri'], media: ['Média', 'b-warn'], alta: ['Alta', 'b-bad'] };

GM.cartaoOcorrencia = (o, fiscal, comComite = false) => {
  const [st, stCls] = GM.STATUS_OC[o.status], [gr, grCls] = GM.GRAV_OC[o.gravidade];
  const podeResponder = fiscal || o.status !== 'resolvida';
  return `<article class="ocorr ${o.status}" data-oc="${o.id}">
    <div class="row" style="gap:6px"><span class="badge ${stCls}">${st}</span><span class="badge ${grCls}">Gravidade ${gr.toLowerCase()}</span><strong>${esc(GM.TIPOS_OC[o.tipo] || o.tipo)}</strong>
      <span class="muted small right">${GM.data(o.criada_em)}</span></div>
    ${comComite ? `<p class="small" style="margin:6px 0 0"><a href="acompanhamento.html?id=${o.comite_id}#ocorrencias">${esc(String(o.comite_nome || '').replace('Comitê de cooperação — ', ''))}</a></p>` : ''}
    ${o.tarefa_titulo ? `<p class="small muted" style="margin:4px 0 0">Etapa ${o.tarefa_ordem}: ${esc(o.tarefa_titulo)}</p>` : ''}
    <p style="margin:8px 0">${esc(o.descricao)}</p>
    <p class="small muted" style="margin:0">Registrada por ${esc(o.autor)}${o.resolvida_em ? ` · resolvida em ${GM.data(o.resolvida_em)}` : ''}</p>
    ${o.respostas.length ? `<ul class="ul-plain ocorr-resp">${o.respostas.map((r) => `<li><span class="small muted">${esc(r.autor)} · ${esc(r.orgao)} · ${GM.data(r.criada_em)}</span><br>${esc(r.texto)}</li>`).join('')}</ul>` : ''}
    ${podeResponder ? `<form class="row ocorr-form" data-oc-resp="${o.id}"><input style="flex:1;min-width:180px" placeholder="${fiscal ? 'Comentar com os tribunais…' : 'Responder à fiscalização…'}" maxlength="4000" aria-label="Resposta"><button class="btn btn-sm btn-primary" type="submit">Enviar</button></form>` : ''}
    ${fiscal ? `<div class="row" style="margin-top:8px">${o.status === 'resolvida'
      ? '<button class="btn btn-sm" type="button" data-oc-status="aberta">Reabrir</button>'
      : '<button class="btn btn-sm" type="button" data-oc-status="resolvida">Marcar como resolvida</button>'}</div>` : ''}
  </article>`;
};

/* Ouvintes delegados no elemento principal (não é recriado): responder e resolver/reabrir. */
GM.ligarOcorrencias = (raiz, aoMudar) => {
  raiz.addEventListener('submit', async (e) => {
    const f = e.target.closest('[data-oc-resp]'); if (!f) return;
    e.preventDefault();
    const tx = f.querySelector('input').value.trim(); if (!tx) return;
    try { await GM.api('POST', `/api/ocorrencias/${f.dataset.ocResp}/respostas`, { texto: tx }); GM.toast('Resposta enviada.', 'ok'); await aoMudar(); }
    catch (err) { GM.toast(err.message, 'erro'); }
  });
  raiz.addEventListener('click', async (e) => {
    const b = e.target.closest('[data-oc-status]'); if (!b) return;
    const id = b.closest('[data-oc]').dataset.oc;
    try { await GM.api('PATCH', `/api/ocorrencias/${id}`, { status: b.dataset.ocStatus }); GM.toast(b.dataset.ocStatus === 'resolvida' ? 'Ocorrência marcada como resolvida.' : 'Ocorrência reaberta.', 'ok'); await aoMudar(); }
    catch (err) { GM.toast(err.message, 'erro'); }
  });
};

/* Janela de registro (fiscal). Devolve true se a ocorrência foi criada. */
GM.novaOcorrencia = (comiteId, tarefas, tarefaId) => new Promise((resolve) => {
  const d = document.createElement('dialog');
  d.style.maxWidth = '520px';
  d.setAttribute('aria-labelledby', 'oc-titulo');
  d.innerHTML = `<h2 id="oc-titulo">Registrar ocorrência</h2>
    <form id="oc-f" style="margin-top:12px" novalidate>
      <div class="alert a-bad hidden" id="oc-erro" role="alert" style="margin-bottom:12px"></div>
      <div class="field"><label for="oc-tipo">Tipo</label><select id="oc-tipo">${Object.entries(GM.TIPOS_OC).map(([k, v]) => `<option value="${k}">${v}</option>`).join('')}</select></div>
      <div class="field"><label for="oc-grav">Gravidade</label><select id="oc-grav"><option value="baixa">Baixa</option><option value="media" selected>Média</option><option value="alta">Alta</option></select></div>
      <div class="field"><label for="oc-tar">Etapa do cronograma</label><select id="oc-tar"><option value="">Geral (toda a iniciativa)</option>${tarefas.map((t) => `<option value="${t.id}"${t.id === tarefaId ? ' selected' : ''}>${t.ordem}. ${esc(t.titulo)}</option>`).join('')}</select></div>
      <div class="field"><label class="req" for="oc-desc">Descreva a ocorrência</label><textarea id="oc-desc" rows="4" maxlength="4000" placeholder="Ex.: O termo de referência não informa o quantitativo por órgão."></textarea></div>
      <p class="small muted">Os dois tribunais da iniciativa são avisados no sininho e respondem no Acompanhamento.</p>
      <div class="row"><button class="btn" type="button" data-fechar>Cancelar</button><button class="btn btn-primary" type="submit">Registrar</button></div>
    </form>`;
  let criada = false;
  const erro = (t) => { const e = d.querySelector('#oc-erro'); e.textContent = t; e.classList.remove('hidden'); };
  d.querySelector('#oc-f').onsubmit = async (e) => {
    e.preventDefault();
    const desc = d.querySelector('#oc-desc').value.trim();
    if (desc.length < 10) { erro('Descreva a ocorrência com pelo menos 10 caracteres.'); return; }
    try {
      await GM.api('POST', `/api/comites/${comiteId}/ocorrencias`, { tipo: d.querySelector('#oc-tipo').value, gravidade: d.querySelector('#oc-grav').value, tarefa_id: d.querySelector('#oc-tar').value || null, descricao: desc });
      criada = true; d.close();
    } catch (err) { erro(err.message); }
  };
  d.addEventListener('click', (e) => { if (e.target === d || e.target.closest('[data-fechar]')) d.close(); });
  d.addEventListener('close', () => { d.remove(); resolve(criada); });
  document.body.appendChild(d);
  d.showModal();
});

GM.atualizarSino = async () => {
  const n = document.getElementById('sino-n'), painel = document.getElementById('sino-painel'), btn = document.getElementById('sino');
  if (!n) return;
  const s = GM.sessao(), fiscal = !!(s.usuario && s.usuario.perfil === 'fiscal');
  const nome = (t) => String(t || '').replace('Comitê de cooperação — ', '');
  const itens = [];
  try {
    const [{ comites }, { ocorrencias }] = await Promise.all([GM.api('GET', '/api/comites'), GM.api('GET', '/api/ocorrencias').catch(() => ({ ocorrencias: [] }))]);
    // contratos a 60 dias (alerta) ou 30 dias (crítico) do fim
    comites.forEach((c) => {
      const k = GM.contrato(c.data_fim_contrato);
      if (k && k.nivel !== 'ok') itens.push({ ordem: (k.nivel === 'critico' ? 0 : 1e6) + k.dias, nivel: k.nivel, badge: k.badge, rot: k.rot, titulo: nome(c.nome), texto: k.texto, href: `acompanhamento.html?id=${c.id}#contrato` });
    });
    // gestor: ocorrências abertas esperando resposta; fiscal: ocorrências respondidas esperando conferência
    ocorrencias.filter((o) => o.status === (fiscal ? 'respondida' : 'aberta')).forEach((o) => {
      const crit = o.gravidade === 'alta';
      itens.push({ ordem: (crit ? 0 : 1e6) - o.id, nivel: crit ? 'critico' : 'alerta', badge: GM.GRAV_OC[o.gravidade][1], rot: `Ocorrência · ${GM.TIPOS_OC[o.tipo] || o.tipo}`, titulo: nome(o.comite_nome),
        texto: fiscal ? 'Os tribunais responderam. Confira e encerre.' : (o.descricao.length > 90 ? o.descricao.slice(0, 90) + '…' : o.descricao), href: `acompanhamento.html?id=${o.comite_id}#ocorrencias` });
    });
  } catch { return; /* o sino é opcional */ }
  itens.sort((a, b) => a.ordem - b.ordem);
  const crit = itens.filter((x) => x.nivel === 'critico').length;
  n.textContent = itens.length; n.classList.toggle('hidden', !itens.length); n.classList.toggle('critico', crit > 0);
  btn.classList.toggle('critico', crit > 0);
  btn.setAttribute('aria-label', itens.length ? `Alertas: ${itens.length}` : 'Alertas: nenhum');
  painel.innerHTML = '<h2>Alertas</h2>' + (itens.length
    ? `<ul class="ul-plain">${itens.map((i) => `<li class="sino-item ${i.nivel}"><a href="${i.href}">
        <span class="badge ${i.badge}">${esc(i.rot)}</span><strong>${esc(i.titulo)}</strong><span class="small">${esc(i.texto)}</span></a></li>`).join('')}</ul>`
    : '<p class="muted small">Nenhum alerta no momento (contratos a até 60 dias do fim e ocorrências da fiscalização aparecem aqui).</p>');
};

GM.atualizarBadgeConvites = async () => {
  try {
    const r = await GM.api('GET', '/api/matches?pendentes=1');
    const b = document.getElementById('nav-conv');
    if (b && r.total) { b.textContent = r.total; b.classList.remove('hidden'); }
  } catch { /* badge é opcional */ }
};

/* ---------- peças de interface de matches ---------- */
GM.anel = (n, extra = '') => `<div class="ring ${n >= 85 ? 'r-alto' : n >= 70 ? 'r-medio' : 'r-baixo'} ${extra}" style="--v:${n}" role="img" aria-label="Compatibilidade de ${n}%"><span>${n}%</span></div>`;

GM.estadoMatch = (m) => {
  if (m.status === 'conectado') return { chave: 'conectado', rot: 'Match! Comitê criado', cls: 'b-ok' };
  if (m.status === 'recusado') return { chave: 'recusado', rot: 'Dispensado', cls: '' };
  if (m.minha_decisao === 'conectar') return { chave: 'aguardando', rot: 'Aguardando o outro órgão', cls: 'b-warn' };
  if (m.pedido_recebido) return { chave: 'novo', rot: 'Pedido de conexão recebido', cls: 'b-warn' };
  return { chave: 'novo', rot: 'Para responder', cls: 'b-pri' };
};

GM.valorOuSigilo = (d) => (d.valor_estimado != null ? GM.brl(d.valor_estimado) : (d.valor_sigiloso ? '<span class="sig">🔒 valor sigiloso</span>' : '—'));

GM.cardMatch = (m, acoes = true) => {
  const o = m.outra_demanda, mi = m.minha_demanda, e = GM.estadoMatch(m);
  const eco = m.economia_valor != null ? `Economia estimada ≈ ${GM.brl(m.economia_valor)} (${GM.pct(m.economia_pct)})` : (m.economia_pct != null ? `Ganho de escala estimado ≈ ${GM.pct(m.economia_pct)}` : '');
  const btns = acoes && e.chave === 'novo'
    ? `<button class="btn btn-primary btn-sm" data-acao="conectar" data-id="${m.id}" type="button">${m.pedido_recebido ? 'Aceitar conexão' : 'Conectar'}</button><button class="btn btn-sm" data-acao="recusar" data-id="${m.id}" type="button">Agora não</button>` : '';
  const com = m.comite_id ? `<a class="btn btn-sm" href="comite.html?id=${m.comite_id}">Abrir comitê</a>` : '';
  return `<article class="card match-card">
    ${GM.anel(m.score)}
    <div class="mc-body">
      <div class="mc-top"><h3><a href="match-detalhe.html?id=${m.id}">${esc(mi.descricao)}</a></h3><span class="badge ${e.cls}">${e.rot}</span></div>
      <p class="muted small" style="margin:2px 0 0">com <strong>${esc(o.orgao.sigla)}</strong> · ${esc(o.descricao)} · ${GM.qtd(o)} · ${GM.mes(o)}</p>
      <ul class="chips">${m.motivos.slice(0, 3).map((x) => `<li>${esc(x)}</li>`).join('')}</ul>
      <div class="mc-foot">${btns}${com}<a href="match-detalhe.html?id=${m.id}" class="small">Ver detalhes</a>
        ${eco ? `<span class="eco right">${eco}</span>` : ''}</div>
    </div></article>`;
};

GM.decidir = async (id, decisao) => {
  const r = await GM.api('POST', `/api/matches/${id}/decisao`, { decisao });
  if (r.deu_match) await GM.momentoMatch(r.match, r.pontos_ganhos);
  else if (decisao === 'conectar') GM.toast('Interesse enviado. Você será avisado quando o outro órgão responder.', 'ok');
  else GM.toast('Sugestão dispensada.');
  return r;
};

GM.momentoMatch = (m, pontos) => new Promise((resolve) => {
  const a = m.minha_demanda, b = m.outra_demanda;
  const eco = m.economia_valor != null ? `Economia estimada ≈ ${GM.brl(m.economia_valor)}` : (m.economia_pct != null ? `Ganho de escala ≈ ${GM.pct(m.economia_pct)}` : '');
  const d = document.createElement('dialog');
  d.className = 'match-modal';
  d.setAttribute('aria-labelledby', 'mm-titulo');
  d.innerHTML = `
    <div class="mm-fundo" aria-hidden="true"></div>
    <div class="mm-palco">
      <div class="mm-org mm-a"><small>seu órgão</small><strong>${esc(a.orgao.sigla)}</strong></div>
      <div class="mm-flor" aria-hidden="true">
        <span class="mm-onda"></span><span class="mm-onda o2"></span>
        ${[0, 1, 2, 3, 4, 5, 6, 7].map((i) => `<i class="mm-fagulha" style="--a:${i * 45}deg"></i>`).join('')}
        <img src="logo-flor.png" alt="">
      </div>
      <div class="mm-org mm-b"><small>parceiro</small><strong>${esc(b.orgao.sigla)}</strong></div>
    </div>
    <h2 id="mm-titulo">É um match!</h2>
    <p class="mm-texto"><strong>${esc(a.orgao.sigla)}</strong> e <strong>${esc(b.orgao.sigla)}</strong> querem cooperar em <strong>“${esc(a.descricao)}”</strong>. Criamos um comitê de cooperação com o cronograma sugerido.</p>
    <div class="mm-chips"><span class="badge b-ok">Compatibilidade ${m.score}%</span>${eco ? `<span class="badge b-pri">${eco}</span>` : ''}${pontos ? `<span class="badge b-warn">★ +${pontos} pontos de incentivo</span>` : ''}</div>
    <div class="mm-acoes"><button class="btn" type="button" data-fechar>Depois</button>
      <a class="btn btn-primary" href="comite.html?id=${m.comite_id}" autofocus>Abrir comitê</a></div>`;
  document.body.appendChild(d);
  d.addEventListener('click', (e) => { if (e.target === d || e.target.closest('[data-fechar]')) d.close(); });
  d.addEventListener('close', () => { d.remove(); resolve(); });
  d.showModal();
});

/* ---------- alerta de pedido de conexão recebido ----------
   Fica na tela até o gestor responder (Aceitar / Agora não) ou remover o alerta (×).
   Pedidos removidos são lembrados neste navegador; continuam em Convites. */
GM.chaveAlertas = () => { const s = GM.sessao(); return `gm_alertas_${s.demo ? 'd' : 'r'}_${s.orgao.id}`; };

GM.alertaPedidos = async () => {
  let pedidos;
  try { pedidos = (await GM.api('GET', '/api/matches?pendentes=1')).matches.filter((m) => m.pedido_recebido); }
  catch { return; }
  let caixa = document.getElementById('alertas-pedido');
  if (!caixa) {
    caixa = document.createElement('div');
    caixa.id = 'alertas-pedido';
    caixa.className = 'alertas-pedido';
    caixa.setAttribute('aria-live', 'assertive');
    document.body.appendChild(caixa);
    caixa.addEventListener('click', GM._cliqueAlerta);
  }
  const removidos = GM.armazenar.ler(GM.chaveAlertas(), []);
  const ativos = pedidos.filter((m) => !removidos.includes(m.id));
  // some o que já foi respondido em outro lugar
  caixa.querySelectorAll('[data-pid]').forEach((el) => { if (!ativos.some((m) => String(m.id) === el.dataset.pid)) el.remove(); });
  ativos.forEach((m) => {
    if (caixa.querySelector(`[data-pid="${m.id}"]`)) return;
    const o = m.outra_demanda, mi = m.minha_demanda;
    const el = document.createElement('section');
    el.className = 'alerta-pedido';
    el.dataset.pid = m.id;
    el.setAttribute('role', 'alert');
    el.innerHTML = `
      <button class="ap-x" type="button" data-ap="remover" aria-label="Remover alerta">×</button>
      <img class="ap-flor" src="logo-flor.png" alt="">
      <div class="ap-corpo">
        <span class="badge b-warn">Pedido de conexão</span>
        <h3><strong>${esc(o.orgao.sigla)}</strong> quer conectar com o ${esc(mi.orgao.sigla)}</h3>
        <p class="small muted" style="margin:0">${esc(mi.descricao)} · compatibilidade <strong>${m.score}%</strong>${m.economia_valor != null ? ` · economia ≈ ${GM.brl(m.economia_valor)}` : ''}</p>
        <div class="ap-acoes">
          <button class="btn btn-primary btn-sm" type="button" data-ap="aceitar">Aceitar conexão</button>
          <a class="btn btn-sm" href="match-detalhe.html?id=${m.id}">Ver detalhes</a>
          <button class="btn btn-sm btn-ghost" type="button" data-ap="recusar">Agora não</button>
        </div>
      </div>`;
    caixa.appendChild(el);
  });
};

GM._cliqueAlerta = async (e) => {
  const b = e.target.closest('[data-ap]');
  if (!b) return;
  const el = b.closest('[data-pid]'), id = +el.dataset.pid, acao = b.dataset.ap;
  if (acao === 'remover') {
    const l = GM.armazenar.ler(GM.chaveAlertas(), []); l.push(id); GM.armazenar.gravar(GM.chaveAlertas(), l);
    el.remove();
    return;
  }
  b.disabled = true;
  try {
    await GM.decidir(id, acao === 'aceitar' ? 'conectar' : 'recusar');
    el.remove();
    location.reload();
  } catch (err) { GM.toast(err.message, 'erro'); b.disabled = false; }
};

/* liga os botões "Conectar"/"Agora não" de uma região da tela */
GM.ligarDecisoes = (raiz, aposDecidir) => {
  raiz.addEventListener('click', async (e) => {
    const b = e.target.closest('[data-acao]');
    if (!b) return;
    b.disabled = true;
    try { await GM.decidir(b.dataset.id, b.dataset.acao); if (aposDecidir) await aposDecidir(); GM.atualizarBadgeConvites(); }
    catch (err) { GM.toast(err.message, 'erro'); b.disabled = false; }
  });
};

GM.vazio = (titulo, texto, link) => `<div class="vazio card"><h3>${esc(titulo)}</h3><p>${texto}</p>${link || ''}</div>`;

/* ---------- registros locais (ainda sem suporte no backend) ---------- */
GM.local = {
  chave: (tipo, comiteId) => `gm_${tipo}_${GM.sessao().orgao.id}_${comiteId}`,
  ler(tipo, comiteId) { return GM.armazenar.ler(this.chave(tipo, comiteId), []); },
  adicionar(tipo, comiteId, item) { const l = this.ler(tipo, comiteId); l.push({ ...item, em: new Date().toISOString() }); GM.armazenar.gravar(this.chave(tipo, comiteId), l); return l; },
  remover(tipo, comiteId, idx) { const l = this.ler(tipo, comiteId); l.splice(idx, 1); GM.armazenar.gravar(this.chave(tipo, comiteId), l); return l; },
};

/* =====================================================================
   MODO DEMONSTRAÇÃO — simula a API com dados fictícios (visão do TRE-PB).
   Serve para abrir o front-end sem o servidor Python.
   ===================================================================== */
const Demo = (() => {
  const CHAVE = 'gm_demo_v3';
  const ORG = {
    'TRE-PB': { id: 1, sigla: 'TRE-PB', nome: 'Tribunal Regional Eleitoral da Paraíba', ramo: 'eleitoral', esfera: 'federal', uf: 'PB', municipio: 'João Pessoa' },
    'TRT 13': { id: 2, sigla: 'TRT 13', nome: 'Tribunal Regional do Trabalho da 13ª Região', ramo: 'trabalho', esfera: 'federal', uf: 'PB', municipio: 'João Pessoa' },
    JFPB: { id: 3, sigla: 'JFPB', nome: 'Justiça Federal na Paraíba', ramo: 'federal', esfera: 'federal', uf: 'PB', municipio: 'João Pessoa' },
    TJPB: { id: 4, sigla: 'TJPB', nome: 'Tribunal de Justiça da Paraíba', ramo: 'estadual', esfera: 'estadual', uf: 'PB', municipio: 'João Pessoa' },
    'TRE-RN': { id: 5, sigla: 'TRE-RN', nome: 'Tribunal Regional Eleitoral do Rio Grande do Norte', ramo: 'eleitoral', esfera: 'federal', uf: 'RN', municipio: 'Natal' },
  };
  const FISCAL_ORG = { id: 99, sigla: 'FISCAL', nome: 'Fiscalização das Contratações', ramo: 'fiscalizacao', esfera: 'federal', uf: 'PB', municipio: 'João Pessoa' };
  // O fiscal só acessa comitês, ocorrências e a própria sessão (igual à API).
  const FISCAL_OK = [['GET', /^\/api\/(me|comites(\/\d+)?|ocorrencias)$/], ['POST', /^\/api\/(comites\/\d+\/ocorrencias|ocorrencias\/\d+\/respostas)$/], ['PATCH', /^\/api\/ocorrencias\/\d+$/]];
  const OC_TIPOS = ['inconsistencia', 'falha', 'falta_informacao', 'intercorrencia'];
  const NB = ['eficiência energética', 'logística reversa', 'restrição de substâncias perigosas'];
  const SOLAR = ['energia renovável', 'logística reversa de módulos'];
  const AR = ['gás refrigerante de baixo impacto', 'destinação adequada de resíduos'];
  const PAPEL = ['papel reciclado', 'certificação florestal'];
  const F_IRP = 'Lei 14.133/2021, art. 86 (intenção de registro de preços)';
  const F_TSE = 'Res. TSE 23.702/2022, art. 14 (promover compras compartilhadas)';
  const F_PCA = 'Lei 14.133/2021, art. 12, VII (PCA para racionalizar contratações)';

  const dem = (o, p) => ({ ano: 2027, natureza: 'contratacao', tipo: 'material', codigo_catalogo: null, categoria: null, valor_estimado: null, valor_sigiloso: false, municipio: null, uf: null, fim_contrato_atual: null, criterios_sustentaveis: [], origem: 'demo', orgao: ORG[o], ...p });
  const irp = (g, p) => ({ modelo: 'irp', titulo: 'Intenção de Registro de Preços (IRP)', descricao: `${g} como órgão gerenciador e ${p} como participante de uma única licitação por registro de preços.`, gerenciador: g, participantes: [p], fundamentos: [F_IRP, F_TSE, F_PCA] });
  const cap = (g, p) => ({ modelo: 'capacitacao_compartilhada', titulo: 'Capacitação compartilhada', descricao: `Turma ou evento único, organizado pelo ${g} com vagas para o ${p}, formalizado no acordo de cooperação técnica.`, gerenciador: g, participantes: [p], fundamentos: [F_TSE] });
  const interfed = (g, p) => ({ tipo: 'interfederativo', texto: `Órgãos federais não podem aderir a ata gerenciada por órgão estadual, distrital ou municipal (Lei 14.133/2021, art. 86, §8º). Por isso o ${g} foi sugerido como gerenciador. Confirme com a assessoria jurídica a participação do ${p}.` });

  const EXTRA = {"demandas":[{"ano":2027,"natureza":"contratacao","tipo":"servico","codigo_catalogo":"CATSER-DEMO-0404","categoria":"Segurança","descricao":"Vigilância patrimonial armada 24 horas","quantidade":24.0,"unidade":"posto","valor_estimado":2100000.0,"valor_sigiloso":false,"mes_previsto":10,"municipio":null,"uf":null,"fim_contrato_atual":"2027-10-31","criterios_sustentaveis":[]},{"ano":2027,"natureza":"contratacao","tipo":"material","codigo_catalogo":"CATMAT-DEMO-0606","categoria":"TIC","descricao":"Cartuchos de toner para impressoras","quantidade":800.0,"unidade":"un","valor_estimado":380000.0,"valor_sigiloso":false,"mes_previsto":4,"municipio":null,"uf":null,"fim_contrato_atual":null,"criterios_sustentaveis":["logística reversa","cartuchos remanufaturados"]},{"ano":2027,"natureza":"contratacao","tipo":"material","codigo_catalogo":"CATMAT-DEMO-0808","categoria":"Mobiliário","descricao":"Cadeiras ergonômicas giratórias","quantidade":150.0,"unidade":"un","valor_estimado":180000.0,"valor_sigiloso":false,"mes_previsto":5,"municipio":null,"uf":null,"fim_contrato_atual":null,"criterios_sustentaveis":["restrição de substâncias perigosas","madeira de origem certificada"]},{"ano":2027,"natureza":"contratacao","tipo":"material","codigo_catalogo":"CATMAT-DEMO-0505","categoria":"Frota","descricao":"Veículos utilitários leves","quantidade":6.0,"unidade":"un","valor_estimado":420000.0,"valor_sigiloso":false,"mes_previsto":7,"municipio":null,"uf":null,"fim_contrato_atual":null,"criterios_sustentaveis":["eficiência energética","baixa emissão de poluentes"]},{"ano":2027,"natureza":"contratacao","tipo":"servico","codigo_catalogo":"CATSER-DEMO-0707","categoria":"TIC","descricao":"Link de internet dedicado","quantidade":4.0,"unidade":"link","valor_estimado":260000.0,"valor_sigiloso":false,"mes_previsto":9,"municipio":null,"uf":null,"fim_contrato_atual":"2027-09-20","criterios_sustentaveis":[]},{"ano":2027,"natureza":"contratacao","tipo":"servico","codigo_catalogo":"CATSER-DEMO-0909","categoria":"Serviços gerais","descricao":"Limpeza e conservação predial","quantidade":8000.0,"unidade":"m2","valor_estimado":640000.0,"valor_sigiloso":false,"mes_previsto":12,"municipio":null,"uf":null,"fim_contrato_atual":"2027-12-31","criterios_sustentaveis":["produtos biodegradáveis","destinação adequada de resíduos"]},{"ano":2027,"natureza":"capacitacao","tipo":"capacitacao","codigo_catalogo":null,"categoria":"Capacitação","descricao":"Curso de inteligência artificial para o setor público","quantidade":30.0,"unidade":"vaga","valor_estimado":null,"valor_sigiloso":false,"mes_previsto":8,"municipio":null,"uf":null,"fim_contrato_atual":null,"criterios_sustentaveis":[]},{"ano":2027,"natureza":"capacitacao","tipo":"capacitacao","codigo_catalogo":null,"categoria":"Capacitação","descricao":"Curso de proteção de dados pessoais e LGPD","quantidade":35.0,"unidade":"vaga","valor_estimado":null,"valor_sigiloso":false,"mes_previsto":4,"municipio":null,"uf":null,"fim_contrato_atual":null,"criterios_sustentaveis":[]},{"ano":2027,"natureza":"outra","tipo":"outro","codigo_catalogo":null,"categoria":"Gestão documental","descricao":"Projeto conjunto de digitalização de acervo documental","quantidade":1.0,"unidade":"projeto","valor_estimado":300000.0,"valor_sigiloso":false,"mes_previsto":7,"municipio":null,"uf":null,"fim_contrato_atual":null,"criterios_sustentaveis":[]}],"matches":[{"id":9,"score":100,"minha_id":11,"org":"JFPB","outra":{"ano":2027,"natureza":"contratacao","tipo":"servico","codigo_catalogo":"CATSER-DEMO-0909","categoria":"Serviços gerais","descricao":"Limpeza e conservação predial","quantidade":12000.0,"unidade":"m2","valor_estimado":950000.0,"valor_sigiloso":false,"mes_previsto":12,"municipio":null,"uf":null,"fim_contrato_atual":"2027-12-15","criterios_sustentaveis":["produtos biodegradáveis","destinação adequada de resíduos"],"id":200},"componentes":{"similaridade":1.0,"tempo":1.0,"territorio":1.0,"sustentabilidade":1.0},"motivos":["Mesmo item no catálogo (CATSER-DEMO-0909)","Previstas para o mesmo mês no PCA","Os dois em João Pessoa/PB","Critérios sustentáveis em comum: produtos biodegradáveis, destinação adequada de resíduos","Contratos atuais terminam com 16 dias de diferença"],"caminho":{"modelo":"irp","titulo":"Intenção de Registro de Preços (IRP)","descricao":"JFPB como órgão gerenciador e TRE-PB como participante de uma única licitação por registro de preços.","gerenciador":"JFPB","participantes":["TRE-PB"],"fundamentos":["Lei 14.133/2021, art. 86 (intenção de registro de preços)","Res. TSE 23.702/2022, art. 14 (promover compras compartilhadas)","Lei 14.133/2021, art. 12, VII (PCA para racionalizar contratações)"]},"alertas":[],"volume_total":20000.0,"economia_pct":0.119,"economia_valor":189210.0,"extra":{}},{"id":10,"score":98,"minha_id":6,"org":"TJPB","outra":{"ano":2027,"natureza":"contratacao","tipo":"servico","codigo_catalogo":"CATSER-DEMO-0404","categoria":"Segurança","descricao":"Vigilância patrimonial armada 24 horas","quantidade":40.0,"unidade":"posto","valor_estimado":4200000.0,"valor_sigiloso":false,"mes_previsto":10,"municipio":null,"uf":null,"fim_contrato_atual":"2027-10-15","criterios_sustentaveis":[],"id":201},"componentes":{"similaridade":1.0,"tempo":1.0,"territorio":1.0,"sustentabilidade":0.5},"motivos":["Mesmo item no catálogo (CATSER-DEMO-0404)","Previstas para o mesmo mês no PCA","Os dois em João Pessoa/PB","Contratos atuais terminam com 16 dias de diferença"],"caminho":{"modelo":"irp","titulo":"Intenção de Registro de Preços (IRP)","descricao":"TRE-PB como órgão gerenciador e TJPB como participante de uma única licitação por registro de preços.","gerenciador":"TRE-PB","participantes":["TJPB"],"fundamentos":["Lei 14.133/2021, art. 86 (intenção de registro de preços)","Res. TSE 23.702/2022, art. 14 (promover compras compartilhadas)","Lei 14.133/2021, art. 12, VII (PCA para racionalizar contratações)"]},"alertas":[{"tipo":"interfederativo","texto":"Órgãos federais não podem aderir a ata gerenciada por órgão estadual, distrital ou municipal (Lei 14.133/2021, art. 86, §8º). Por isso o TRE-PB foi sugerido como gerenciador. Confirme com a assessoria jurídica a participação do TJPB."}],"volume_total":64.0,"economia_pct":0.114,"economia_valor":718200.0,"extra":{"outro_conectou":true}},{"id":11,"score":96,"minha_id":8,"org":"TRT 13","outra":{"ano":2027,"natureza":"contratacao","tipo":"material","codigo_catalogo":"CATMAT-DEMO-0808","categoria":"Mobiliário","descricao":"Cadeiras ergonômicas giratórias","quantidade":120.0,"unidade":"un","valor_estimado":150000.0,"valor_sigiloso":false,"mes_previsto":6,"municipio":null,"uf":null,"fim_contrato_atual":null,"criterios_sustentaveis":["restrição de substâncias perigosas","madeira de origem certificada"],"id":202},"componentes":{"similaridade":1.0,"tempo":0.833,"territorio":1.0,"sustentabilidade":1.0},"motivos":["Mesmo item no catálogo (CATMAT-DEMO-0808)","Previsões no PCA com 1 mês de diferença","Os dois em João Pessoa/PB","Critérios sustentáveis em comum: restrição de substâncias perigosas, madeira de origem certificada"],"caminho":{"modelo":"irp","titulo":"Intenção de Registro de Preços (IRP)","descricao":"TRE-PB como órgão gerenciador e TRT 13 como participante de uma única licitação por registro de preços.","gerenciador":"TRE-PB","participantes":["TRT 13"],"fundamentos":["Lei 14.133/2021, art. 86 (intenção de registro de preços)","Res. TSE 23.702/2022, art. 14 (promover compras compartilhadas)","Lei 14.133/2021, art. 12, VII (PCA para racionalizar contratações)"]},"alertas":[],"volume_total":270.0,"economia_pct":0.128,"economia_valor":42240.0,"extra":{}},{"id":12,"score":96,"minha_id":7,"org":"TRT 13","outra":{"ano":2027,"natureza":"contratacao","tipo":"material","codigo_catalogo":"CATMAT-DEMO-0606","categoria":"TIC","descricao":"Cartuchos de toner para impressoras","quantidade":500.0,"unidade":"un","valor_estimado":240000.0,"valor_sigiloso":false,"mes_previsto":5,"municipio":null,"uf":null,"fim_contrato_atual":null,"criterios_sustentaveis":["logística reversa","cartuchos remanufaturados"],"id":203},"componentes":{"similaridade":1.0,"tempo":0.833,"territorio":1.0,"sustentabilidade":1.0},"motivos":["Mesmo item no catálogo (CATMAT-DEMO-0606)","Previsões no PCA com 1 mês de diferença","Os dois em João Pessoa/PB","Critérios sustentáveis em comum: logística reversa, cartuchos remanufaturados"],"caminho":{"modelo":"irp","titulo":"Intenção de Registro de Preços (IRP)","descricao":"TRE-PB como órgão gerenciador e TRT 13 como participante de uma única licitação por registro de preços.","gerenciador":"TRE-PB","participantes":["TRT 13"],"fundamentos":["Lei 14.133/2021, art. 86 (intenção de registro de preços)","Res. TSE 23.702/2022, art. 14 (promover compras compartilhadas)","Lei 14.133/2021, art. 12, VII (PCA para racionalizar contratações)"]},"alertas":[],"volume_total":1300.0,"economia_pct":0.116,"economia_valor":71920.0,"extra":{"status":"recusado","minha_decisao":"recusar"}},{"id":13,"score":96,"minha_id":7,"org":"TJPB","outra":{"ano":2027,"natureza":"contratacao","tipo":"material","codigo_catalogo":"CATMAT-DEMO-0606","categoria":"TIC","descricao":"Cartuchos de toner para impressoras","quantidade":1500.0,"unidade":"un","valor_estimado":700000.0,"valor_sigiloso":false,"mes_previsto":3,"municipio":null,"uf":null,"fim_contrato_atual":null,"criterios_sustentaveis":["logística reversa","cartuchos remanufaturados"],"id":204},"componentes":{"similaridade":1.0,"tempo":0.833,"territorio":1.0,"sustentabilidade":1.0},"motivos":["Mesmo item no catálogo (CATMAT-DEMO-0606)","Previsões no PCA com 1 mês de diferença","Os dois em João Pessoa/PB","Critérios sustentáveis em comum: logística reversa, cartuchos remanufaturados"],"caminho":{"modelo":"irp","titulo":"Intenção de Registro de Preços (IRP)","descricao":"TRE-PB como órgão gerenciador e TJPB como participante de uma única licitação por registro de preços.","gerenciador":"TRE-PB","participantes":["TJPB"],"fundamentos":["Lei 14.133/2021, art. 86 (intenção de registro de preços)","Res. TSE 23.702/2022, art. 14 (promover compras compartilhadas)","Lei 14.133/2021, art. 12, VII (PCA para racionalizar contratações)"]},"alertas":[{"tipo":"interfederativo","texto":"Órgãos federais não podem aderir a ata gerenciada por órgão estadual, distrital ou municipal (Lei 14.133/2021, art. 86, §8º). Por isso o TRE-PB foi sugerido como gerenciador. Confirme com a assessoria jurídica a participação do TJPB."}],"volume_total":2300.0,"economia_pct":0.109,"economia_valor":117720.0,"extra":{}},{"id":14,"score":96,"minha_id":9,"org":"JFPB","outra":{"ano":2027,"natureza":"contratacao","tipo":"material","codigo_catalogo":"CATMAT-DEMO-0505","categoria":"Frota","descricao":"Veículos utilitários leves","quantidade":8.0,"unidade":"un","valor_estimado":560000.0,"valor_sigiloso":false,"mes_previsto":8,"municipio":null,"uf":null,"fim_contrato_atual":null,"criterios_sustentaveis":["eficiência energética","baixa emissão de poluentes"],"id":205},"componentes":{"similaridade":1.0,"tempo":0.833,"territorio":1.0,"sustentabilidade":1.0},"motivos":["Mesmo item no catálogo (CATMAT-DEMO-0505)","Previsões no PCA com 1 mês de diferença","Os dois em João Pessoa/PB","Critérios sustentáveis em comum: eficiência energética, baixa emissão de poluentes"],"caminho":{"modelo":"irp","titulo":"Intenção de Registro de Preços (IRP)","descricao":"TRE-PB como órgão gerenciador e JFPB como participante de uma única licitação por registro de preços.","gerenciador":"TRE-PB","participantes":["JFPB"],"fundamentos":["Lei 14.133/2021, art. 86 (intenção de registro de preços)","Res. TSE 23.702/2022, art. 14 (promover compras compartilhadas)","Lei 14.133/2021, art. 12, VII (PCA para racionalizar contratações)"]},"alertas":[],"volume_total":14.0,"economia_pct":0.125,"economia_valor":122500.0,"extra":{"minha_decisao":"conectar"}},{"id":15,"score":93,"minha_id":10,"org":"JFPB","outra":{"ano":2027,"natureza":"contratacao","tipo":"servico","codigo_catalogo":"CATSER-DEMO-0707","categoria":"TIC","descricao":"Link de internet dedicado","quantidade":3.0,"unidade":"link","valor_estimado":210000.0,"valor_sigiloso":false,"mes_previsto":10,"municipio":null,"uf":null,"fim_contrato_atual":"2027-10-05","criterios_sustentaveis":[],"id":206},"componentes":{"similaridade":1.0,"tempo":0.833,"territorio":1.0,"sustentabilidade":0.5},"motivos":["Mesmo item no catálogo (CATSER-DEMO-0707)","Previsões no PCA com 1 mês de diferença","Os dois em João Pessoa/PB","Contratos atuais terminam com 15 dias de diferença"],"caminho":{"modelo":"irp","titulo":"Intenção de Registro de Preços (IRP)","descricao":"TRE-PB como órgão gerenciador e JFPB como participante de uma única licitação por registro de preços.","gerenciador":"TRE-PB","participantes":["JFPB"],"fundamentos":["Lei 14.133/2021, art. 86 (intenção de registro de preços)","Res. TSE 23.702/2022, art. 14 (promover compras compartilhadas)","Lei 14.133/2021, art. 12, VII (PCA para racionalizar contratações)"]},"alertas":[],"volume_total":7.0,"economia_pct":0.125,"economia_valor":58750.0,"extra":{}},{"id":16,"score":93,"minha_id":6,"org":"TRT 13","outra":{"ano":2027,"natureza":"contratacao","tipo":"servico","codigo_catalogo":"CATSER-DEMO-0404","categoria":"Segurança","descricao":"Vigilância patrimonial armada 24 horas","quantidade":18.0,"unidade":"posto","valor_estimado":1650000.0,"valor_sigiloso":false,"mes_previsto":11,"municipio":null,"uf":null,"fim_contrato_atual":"2027-11-30","criterios_sustentaveis":[],"id":207},"componentes":{"similaridade":1.0,"tempo":0.833,"territorio":1.0,"sustentabilidade":0.5},"motivos":["Mesmo item no catálogo (CATSER-DEMO-0404)","Previsões no PCA com 1 mês de diferença","Os dois em João Pessoa/PB","Contratos atuais terminam com 30 dias de diferença"],"caminho":{"modelo":"irp","titulo":"Intenção de Registro de Preços (IRP)","descricao":"TRE-PB como órgão gerenciador e TRT 13 como participante de uma única licitação por registro de preços.","gerenciador":"TRE-PB","participantes":["TRT 13"],"fundamentos":["Lei 14.133/2021, art. 86 (intenção de registro de preços)","Res. TSE 23.702/2022, art. 14 (promover compras compartilhadas)","Lei 14.133/2021, art. 12, VII (PCA para racionalizar contratações)"]},"alertas":[],"volume_total":42.0,"economia_pct":0.125,"economia_valor":468750.0,"extra":{}},{"id":17,"score":92,"minha_id":12,"org":"TJPB","outra":{"ano":2027,"natureza":"capacitacao","tipo":"capacitacao","codigo_catalogo":null,"categoria":"Capacitação","descricao":"Curso de inteligência artificial para o setor público","quantidade":60.0,"unidade":"vaga","valor_estimado":null,"valor_sigiloso":false,"mes_previsto":8,"municipio":null,"uf":null,"fim_contrato_atual":null,"criterios_sustentaveis":[],"id":208},"componentes":{"similaridade":1.0,"tempo":1.0,"territorio":1.0,"sustentabilidade":0.5},"motivos":["Descrições compatíveis (100% dos termos em comum)","Previstas para o mesmo mês no PCA","Os dois em João Pessoa/PB"],"caminho":{"modelo":"capacitacao_compartilhada","titulo":"Capacitação compartilhada","descricao":"Turma ou evento único, organizado pelo TRE-PB com vagas para o TJPB, formalizado no acordo de cooperação técnica.","gerenciador":"TRE-PB","participantes":["TJPB"],"fundamentos":["Res. TSE 23.702/2022, art. 14 (promover compras compartilhadas)"]},"alertas":[],"volume_total":90.0,"economia_pct":0.107,"economia_valor":null,"extra":{}},{"id":18,"score":92,"minha_id":13,"org":"TJPB","outra":{"ano":2027,"natureza":"capacitacao","tipo":"capacitacao","codigo_catalogo":null,"categoria":"Capacitação","descricao":"Curso de proteção de dados pessoais e LGPD","quantidade":50.0,"unidade":"vaga","valor_estimado":null,"valor_sigiloso":false,"mes_previsto":4,"municipio":null,"uf":null,"fim_contrato_atual":null,"criterios_sustentaveis":[],"id":209},"componentes":{"similaridade":1.0,"tempo":1.0,"territorio":1.0,"sustentabilidade":0.5},"motivos":["Descrições compatíveis (100% dos termos em comum)","Previstas para o mesmo mês no PCA","Os dois em João Pessoa/PB"],"caminho":{"modelo":"capacitacao_compartilhada","titulo":"Capacitação compartilhada","descricao":"Turma ou evento único, organizado pelo TRE-PB com vagas para o TJPB, formalizado no acordo de cooperação técnica.","gerenciador":"TRE-PB","participantes":["TJPB"],"fundamentos":["Res. TSE 23.702/2022, art. 14 (promover compras compartilhadas)"]},"alertas":[],"volume_total":85.0,"economia_pct":0.121,"economia_valor":null,"extra":{"outro_conectou":true}},{"id":19,"score":92,"minha_id":9,"org":"TRE-RN","outra":{"ano":2027,"natureza":"contratacao","tipo":"material","codigo_catalogo":"CATMAT-DEMO-0505","categoria":"Frota","descricao":"Veículos utilitários leves","quantidade":10.0,"unidade":"un","valor_estimado":700000.0,"valor_sigiloso":false,"mes_previsto":7,"municipio":null,"uf":null,"fim_contrato_atual":null,"criterios_sustentaveis":["eficiência energética","baixa emissão de poluentes"],"id":210},"componentes":{"similaridade":1.0,"tempo":1.0,"territorio":0.5,"sustentabilidade":1.0},"motivos":["Mesmo item no catálogo (CATMAT-DEMO-0505)","Previstas para o mesmo mês no PCA","Estados diferentes (PB e RN)","Critérios sustentáveis em comum: eficiência energética, baixa emissão de poluentes"],"caminho":{"modelo":"irp","titulo":"Intenção de Registro de Preços (IRP)","descricao":"TRE-RN como órgão gerenciador e TRE-PB como participante de uma única licitação por registro de preços.","gerenciador":"TRE-RN","participantes":["TRE-PB"],"fundamentos":["Lei 14.133/2021, art. 86 (intenção de registro de preços)","Res. TSE 23.702/2022, art. 14 (promover compras compartilhadas)","Lei 14.133/2021, art. 12, VII (PCA para racionalizar contratações)"]},"alertas":[],"volume_total":16.0,"economia_pct":0.114,"economia_valor":127680.0,"extra":{}},{"id":20,"score":88,"minha_id":12,"org":"TRT 13","outra":{"ano":2027,"natureza":"capacitacao","tipo":"capacitacao","codigo_catalogo":null,"categoria":"Capacitação","descricao":"Curso de inteligência artificial para o setor público","quantidade":45.0,"unidade":"vaga","valor_estimado":null,"valor_sigiloso":false,"mes_previsto":9,"municipio":null,"uf":null,"fim_contrato_atual":null,"criterios_sustentaveis":[],"id":211},"componentes":{"similaridade":1.0,"tempo":0.833,"territorio":1.0,"sustentabilidade":0.5},"motivos":["Descrições compatíveis (100% dos termos em comum)","Previsões no PCA com 1 mês de diferença","Os dois em João Pessoa/PB"],"caminho":{"modelo":"capacitacao_compartilhada","titulo":"Capacitação compartilhada","descricao":"Turma ou evento único, organizado pelo TRE-PB com vagas para o TRT 13, formalizado no acordo de cooperação técnica.","gerenciador":"TRE-PB","participantes":["TRT 13"],"fundamentos":["Res. TSE 23.702/2022, art. 14 (promover compras compartilhadas)"]},"alertas":[],"volume_total":75.0,"economia_pct":0.119,"economia_valor":null,"extra":{}},{"id":21,"score":88,"minha_id":13,"org":"JFPB","outra":{"ano":2027,"natureza":"capacitacao","tipo":"capacitacao","codigo_catalogo":null,"categoria":"Capacitação","descricao":"Curso de proteção de dados pessoais e LGPD","quantidade":20.0,"unidade":"vaga","valor_estimado":null,"valor_sigiloso":false,"mes_previsto":5,"municipio":null,"uf":null,"fim_contrato_atual":null,"criterios_sustentaveis":[],"id":212},"componentes":{"similaridade":1.0,"tempo":0.833,"territorio":1.0,"sustentabilidade":0.5},"motivos":["Descrições compatíveis (100% dos termos em comum)","Previsões no PCA com 1 mês de diferença","Os dois em João Pessoa/PB"],"caminho":{"modelo":"capacitacao_compartilhada","titulo":"Capacitação compartilhada","descricao":"Turma ou evento único, organizado pelo TRE-PB com vagas para o JFPB, formalizado no acordo de cooperação técnica.","gerenciador":"TRE-PB","participantes":["JFPB"],"fundamentos":["Res. TSE 23.702/2022, art. 14 (promover compras compartilhadas)"]},"alertas":[],"volume_total":55.0,"economia_pct":0.112,"economia_valor":null,"extra":{}},{"id":22,"score":88,"minha_id":14,"org":"TRT 13","outra":{"ano":2027,"natureza":"outra","tipo":"outro","codigo_catalogo":null,"categoria":"Gestão documental","descricao":"Projeto conjunto de digitalização de acervo documental","quantidade":1.0,"unidade":"projeto","valor_estimado":420000.0,"valor_sigiloso":false,"mes_previsto":8,"municipio":null,"uf":null,"fim_contrato_atual":null,"criterios_sustentaveis":[],"id":213},"componentes":{"similaridade":1.0,"tempo":0.833,"territorio":1.0,"sustentabilidade":0.5},"motivos":["Descrições compatíveis (100% dos termos em comum)","Previsões no PCA com 1 mês de diferença","Os dois em João Pessoa/PB"],"caminho":{"modelo":"irp","titulo":"Intenção de Registro de Preços (IRP)","descricao":"TRE-PB como órgão gerenciador e TRT 13 como participante de uma única licitação por registro de preços.","gerenciador":"TRE-PB","participantes":["TRT 13"],"fundamentos":["Lei 14.133/2021, art. 86 (intenção de registro de preços)","Res. TSE 23.702/2022, art. 14 (promover compras compartilhadas)","Lei 14.133/2021, art. 12, VII (PCA para racionalizar contratações)"]},"alertas":[],"volume_total":2.0,"economia_pct":0.14,"economia_valor":100800.0,"extra":{}},{"id":23,"score":85,"minha_id":7,"org":"TRE-RN","outra":{"ano":2027,"natureza":"contratacao","tipo":"material","codigo_catalogo":"CATMAT-DEMO-0606","categoria":"TIC","descricao":"Cartuchos de toner para impressoras","quantidade":400.0,"unidade":"un","valor_estimado":190000.0,"valor_sigiloso":false,"mes_previsto":4,"municipio":null,"uf":null,"fim_contrato_atual":null,"criterios_sustentaveis":["logística reversa"],"id":214},"componentes":{"similaridade":1.0,"tempo":1.0,"territorio":0.5,"sustentabilidade":0.5},"motivos":["Mesmo item no catálogo (CATMAT-DEMO-0606)","Previstas para o mesmo mês no PCA","Estados diferentes (PB e RN)","Critérios sustentáveis em comum: logística reversa"],"caminho":{"modelo":"irp","titulo":"Intenção de Registro de Preços (IRP)","descricao":"TRE-PB como órgão gerenciador e TRE-RN como participante de uma única licitação por registro de preços.","gerenciador":"TRE-PB","participantes":["TRE-RN"],"fundamentos":["Lei 14.133/2021, art. 86 (intenção de registro de preços)","Res. TSE 23.702/2022, art. 14 (promover compras compartilhadas)","Lei 14.133/2021, art. 12, VII (PCA para racionalizar contratações)"]},"alertas":[],"volume_total":1200.0,"economia_pct":0.107,"economia_valor":60990.0,"extra":{}},{"id":24,"score":84,"minha_id":12,"org":"TRE-RN","outra":{"ano":2027,"natureza":"capacitacao","tipo":"capacitacao","codigo_catalogo":null,"categoria":"Capacitação","descricao":"Curso de inteligência artificial para o setor público","quantidade":25.0,"unidade":"vaga","valor_estimado":null,"valor_sigiloso":false,"mes_previsto":8,"municipio":null,"uf":null,"fim_contrato_atual":null,"criterios_sustentaveis":[],"id":215},"componentes":{"similaridade":1.0,"tempo":1.0,"territorio":0.4,"sustentabilidade":0.5},"motivos":["Descrições compatíveis (100% dos termos em comum)","Previstas para o mesmo mês no PCA","Estados diferentes (PB e RN)"],"caminho":{"modelo":"capacitacao_compartilhada","titulo":"Capacitação compartilhada","descricao":"Turma ou evento único, organizado pelo TRE-PB com vagas para o TRE-RN, formalizado no acordo de cooperação técnica.","gerenciador":"TRE-PB","participantes":["TRE-RN"],"fundamentos":["Res. TSE 23.702/2022, art. 14 (promover compras compartilhadas)"]},"alertas":[],"volume_total":55.0,"economia_pct":0.13,"economia_valor":null,"extra":{}},{"id":25,"score":76,"minha_id":8,"org":"TJPB","outra":{"ano":2027,"natureza":"contratacao","tipo":"material","codigo_catalogo":"CATMAT-DEMO-0808","categoria":"Mobiliário","descricao":"Cadeiras ergonômicas giratórias","quantidade":300.0,"unidade":"un","valor_estimado":330000.0,"valor_sigiloso":false,"mes_previsto":9,"municipio":null,"uf":null,"fim_contrato_atual":null,"criterios_sustentaveis":["restrição de substâncias perigosas"],"id":216},"componentes":{"similaridade":1.0,"tempo":0.333,"territorio":1.0,"sustentabilidade":0.5},"motivos":["Mesmo item no catálogo (CATMAT-DEMO-0808)","Previsões no PCA com 4 meses de diferença","Os dois em João Pessoa/PB","Critérios sustentáveis em comum: restrição de substâncias perigosas"],"caminho":{"modelo":"irp","titulo":"Intenção de Registro de Preços (IRP)","descricao":"TRE-PB como órgão gerenciador e TJPB como participante de uma única licitação por registro de preços.","gerenciador":"TRE-PB","participantes":["TJPB"],"fundamentos":["Lei 14.133/2021, art. 86 (intenção de registro de preços)","Res. TSE 23.702/2022, art. 14 (promover compras compartilhadas)","Lei 14.133/2021, art. 12, VII (PCA para racionalizar contratações)"]},"alertas":[{"tipo":"interfederativo","texto":"Órgãos federais não podem aderir a ata gerenciada por órgão estadual, distrital ou municipal (Lei 14.133/2021, art. 86, §8º). Por isso o TRE-PB foi sugerido como gerenciador. Confirme com a assessoria jurídica a participação do TJPB."},{"tipo":"prazo","texto":"As previsões estão 4 meses distantes: um dos órgãos precisará ajustar o cronograma do PCA."}],"volume_total":450.0,"economia_pct":0.107,"economia_valor":54570.0,"extra":{}}]};

  function inicial() {
    const minhas = [
      dem('TRE-PB', { id: 1, descricao: 'Notebooks corporativos', codigo_catalogo: 'CATMAT-DEMO-0001', categoria: 'TIC', quantidade: 120, unidade: 'un', valor_estimado: 760000, mes_previsto: 3, criterios_sustentaveis: NB }),
      dem('TRE-PB', { id: 2, descricao: 'Usina solar fotovoltaica em prédio próprio', codigo_catalogo: 'CATSER-DEMO-0101', categoria: 'Energia', tipo: 'servico', quantidade: 300, unidade: 'kWp', valor_estimado: 1600000, mes_previsto: 6, criterios_sustentaveis: SOLAR }),
      dem('TRE-PB', { id: 3, descricao: 'Manutenção preventiva e corretiva de ar-condicionado', codigo_catalogo: 'CATSER-DEMO-0202', categoria: 'Manutenção', tipo: 'servico', quantidade: 260, unidade: 'equipamento', valor_estimado: 900000, mes_previsto: 8, fim_contrato_atual: '2027-08-31', criterios_sustentaveis: AR }),
      dem('TRE-PB', { id: 4, descricao: 'Papel A4 reciclado', codigo_catalogo: 'CATMAT-DEMO-0003', categoria: 'Expediente', quantidade: 2000, unidade: 'resma', valor_estimado: 50000, mes_previsto: 2, criterios_sustentaveis: PAPEL }),
      dem('TRE-PB', { id: 5, descricao: 'Curso de fiscalização de contratos na Lei 14.133', natureza: 'capacitacao', tipo: 'capacitacao', categoria: 'Capacitação', quantidade: 40, unidade: 'vaga', mes_previsto: 5 }),
    ];
    const M = (id, score, minha_id, outra, componentes, motivos, caminho, alertas, vol, pct, valor, extra) => ({
      id, score, minha_id, outra, componentes, motivos, caminho, alertas, volume_total: vol, economia_pct: pct, economia_valor: valor,
      status: 'sugerido', minha_decisao: null, outro_conectou: false, comite_id: null, atualizado_em: '2026-11-10T09:00:00', ...extra,
    });
    const matches = [
      M(1, 96, 1, dem('TRT 13', { id: 101, descricao: 'Notebooks corporativos', codigo_catalogo: 'CATMAT-DEMO-0001', categoria: 'TIC', quantidade: 180, unidade: 'un', valor_estimado: 1140000, mes_previsto: 4, criterios_sustentaveis: NB }),
        { similaridade: 1, tempo: .833, territorio: 1, sustentabilidade: 1 },
        ['Mesmo item no catálogo (CATMAT-DEMO-0001)', 'Previsões no PCA com 1 mês de diferença', 'Os dois em João Pessoa/PB', 'Critérios sustentáveis em comum: eficiência energética, logística reversa, restrição de substâncias perigosas'],
        irp('TRE-PB', 'TRT 13'), [], 300, .119, 226100, { status: 'conectado', minha_decisao: 'conectar', comite_id: 1 }),
      M(2, 87, 1, dem('TJPB', { id: 102, descricao: 'Notebooks corporativos', codigo_catalogo: 'CATMAT-DEMO-0001', categoria: 'TIC', quantidade: 250, unidade: 'un', valor_estimado: 1500000, mes_previsto: 5, criterios_sustentaveis: NB.slice(0, 2) }),
        { similaridade: 1, tempo: .667, territorio: 1, sustentabilidade: .667 },
        ['Mesmo item no catálogo (CATMAT-DEMO-0001)', 'Previsões no PCA com 2 meses de diferença', 'Os dois em João Pessoa/PB', 'Critérios sustentáveis em comum: eficiência energética, logística reversa'],
        irp('TRE-PB', 'TJPB'), [interfed('TRE-PB', 'TJPB')], 370, .105, 237300, { outro_conectou: true }),
      M(3, 92, 1, dem('TRE-RN', { id: 103, descricao: 'Notebooks corporativos', codigo_catalogo: 'CATMAT-DEMO-0001', categoria: 'TIC', quantidade: 90, unidade: 'un', valor_estimado: 560000, mes_previsto: 3, criterios_sustentaveis: NB }),
        { similaridade: 1, tempo: 1, territorio: .5, sustentabilidade: 1 },
        ['Mesmo item no catálogo (CATMAT-DEMO-0001)', 'Previstas para o mesmo mês no PCA', 'Estados diferentes (PB e RN)', 'Critérios sustentáveis em comum: eficiência energética, logística reversa, restrição de substâncias perigosas'],
        irp('TRE-PB', 'TRE-RN'), [], 210, .125, 165000, { outro_conectou: true }),
      M(4, 100, 2, dem('TJPB', { id: 104, descricao: 'Usina solar fotovoltaica em prédios próprios', codigo_catalogo: 'CATSER-DEMO-0101', categoria: 'Energia', tipo: 'servico', quantidade: 900, unidade: 'kWp', valor_estimado: null, valor_sigiloso: true, mes_previsto: 6, criterios_sustentaveis: SOLAR }),
        { similaridade: 1, tempo: 1, territorio: 1, sustentabilidade: 1 },
        ['Mesmo item no catálogo (CATSER-DEMO-0101)', 'Previstas para o mesmo mês no PCA', 'Os dois em João Pessoa/PB', 'Critérios sustentáveis em comum: energia renovável, logística reversa de módulos'],
        irp('TRE-PB', 'TJPB'), [interfed('TRE-PB', 'TJPB')], 1200, .093, null, {}),
      M(5, 100, 3, dem('JFPB', { id: 105, descricao: 'Manutenção preventiva e corretiva de ar-condicionado', codigo_catalogo: 'CATSER-DEMO-0202', categoria: 'Manutenção', tipo: 'servico', quantidade: 380, unidade: 'equipamento', valor_estimado: 1400000, mes_previsto: 9, fim_contrato_atual: '2027-09-30', criterios_sustentaveis: AR }),
        { similaridade: 1, tempo: .833, territorio: 1, sustentabilidade: 1 },
        ['Mesmo item no catálogo (CATSER-DEMO-0202)', 'Previsões no PCA com 1 mês de diferença', 'Os dois em João Pessoa/PB', 'Critérios sustentáveis em comum: gás refrigerante de baixo impacto, destinação adequada de resíduos', 'Contratos atuais terminam com 30 dias de diferença'],
        irp('TRE-PB', 'JFPB'), [], 640, .12, 276000, { minha_decisao: 'conectar' }),
      M(6, 96, 4, dem('TJPB', { id: 106, descricao: 'Papel A4 reciclado', codigo_catalogo: 'CATMAT-DEMO-0003', categoria: 'Expediente', quantidade: 3000, unidade: 'resma', valor_estimado: 70000, mes_previsto: 3, criterios_sustentaveis: PAPEL }),
        { similaridade: 1, tempo: .833, territorio: 1, sustentabilidade: 1 },
        ['Mesmo item no catálogo (CATMAT-DEMO-0003)', 'Previsões no PCA com 1 mês de diferença', 'Os dois em João Pessoa/PB', 'Critérios sustentáveis em comum: papel reciclado, certificação florestal'],
        irp('TRE-PB', 'TJPB'), [interfed('TRE-PB', 'TJPB'), { tipo: 'me_epp', texto: 'Somados, os valores passam de R$ 80 mil e podem afastar a licitação exclusiva para ME/EPP (LC 123/2006, art. 48, I). Avalie dividir em itens ou usar cota reservada.' }], 5000, .119, 14280, {}),
      M(7, 66, 5, dem('TRT 13', { id: 107, descricao: 'Curso de fiscalização de contratos administrativos', natureza: 'capacitacao', tipo: 'capacitacao', categoria: 'Capacitação', quantidade: 60, unidade: 'vaga', mes_previsto: 6 }),
        { similaridade: .5, tempo: .833, territorio: 1, sustentabilidade: .5 },
        ['Descrições compatíveis (50% dos termos em comum)', 'Previsões no PCA com 1 mês de diferença', 'Os dois em João Pessoa/PB'],
        cap('TRE-PB', 'TRT 13'), [], 100, .119, null, {}),
      M(8, 66, 5, dem('JFPB', { id: 108, descricao: 'Curso de fiscalização de contratos (EAD)', natureza: 'capacitacao', tipo: 'capacitacao', categoria: 'Capacitação', quantidade: 25, unidade: 'vaga', mes_previsto: 6 }),
        { similaridade: .5, tempo: .833, territorio: 1, sustentabilidade: .5 },
        ['Descrições compatíveis (50% dos termos em comum)', 'Previsões no PCA com 1 mês de diferença', 'Os dois em João Pessoa/PB'],
        cap('TRE-PB', 'JFPB'), [], 65, .104, null, { status: 'recusado', minha_decisao: 'recusar' }),
    ];
    EXTRA.demandas.forEach((d) => minhas.push(dem('TRE-PB', { ...d, id: minhas.length + 1 })));
    EXTRA.matches.forEach((x) => matches.push(M(x.id, x.score, x.minha_id, dem(x.org, x.outra), x.componentes, x.motivos, x.caminho, x.alertas, x.volume_total, x.economia_pct, x.economia_valor, x.extra)));
    const comites = [{
      id: 1, match_id: 1, nome: 'Comitê de cooperação — Notebooks corporativos', gerenciador: 'TRE-PB', criado_em: '2026-11-05T10:00:00',
      tarefas: [
        { id: 1, ordem: 1, titulo: 'Alinhar especificação técnica e critérios sustentáveis', resp: null, prazo: '2026-12-01', concluida: true },
        { id: 2, ordem: 2, titulo: 'Elaborar ETP e termo de referência conjuntos', resp: 1, prazo: '2027-01-01', concluida: false },
        { id: 3, ordem: 3, titulo: 'Publicar a IRP (prazo mínimo de 8 dias úteis)', resp: 1, prazo: '2027-02-01', concluida: false },
        { id: 4, ordem: 4, titulo: 'Realizar a licitação', resp: 1, prazo: '2027-03-01', concluida: false },
        { id: 5, ordem: 5, titulo: 'Assinar a ata e emitir o contrato de cada órgão', resp: null, prazo: '2027-04-01', concluida: false },
      ],
      mensagens: [],
    }];
    const ocorrencias = [{ id: 1, comite_id: 1, tarefa_id: 2, tipo: 'falta_informacao', gravidade: 'media', status: 'aberta', autor: 'Fiscal das Contratações',
      descricao: 'O termo de referência ainda não informa o quantitativo de notebooks por órgão. Complementar antes da publicação da IRP.', criada_em: '2026-11-10T09:00:00', resolvida_em: null, respostas: [] }];
    return { demandas: minhas, matches, comites, ocorrencias, prox: { demanda: 6 + EXTRA.demandas.length, comite: 2, tarefa: 6, msg: 3, ocorrencia: 2, resposta: 1 } };
  }

  const clone = (x) => JSON.parse(JSON.stringify(x));
  const ler = () => {
    let s = GM.armazenar.ler(CHAVE, null);
    if (!s) { s = inicial(); gravar(s); }
    if (!s.ocorrencias) { const i = inicial(); s.ocorrencias = i.ocorrencias; s.prox = { ...i.prox, ...s.prox }; }  // estado salvo antes das ocorrências
    return s;
  };
  const gravar = (s) => GM.armazenar.gravar(CHAVE, s);
  const erro = (status, msg) => Object.assign(new Error(msg), { status });
  const mesmaOrg = ORG['TRE-PB'];

  const verDemanda = (d) => ({ ...d, orgao: d.orgao || mesmaOrg });
  const verMatch = (S, m) => {
    const outra = clone(m.outra);
    if (outra.valor_sigiloso) outra.valor_estimado = null;
    return { id: m.id, score: m.score, status: m.status, minha_demanda: clone(verDemanda(S.demandas.find((d) => d.id === m.minha_id))), outra_demanda: outra,
      componentes: m.componentes, motivos: m.motivos, caminho: m.caminho, alertas: m.alertas, volume_total: m.volume_total, economia_pct: m.economia_pct,
      economia_valor: m.economia_valor, minha_decisao: m.minha_decisao, comite_id: m.comite_id, atualizado_em: m.atualizado_em,
      pedido_recebido: !!(m.outro_conectou && !m.minha_decisao && m.status === 'sugerido') };
  };
  const verComite = (S, c, completo) => {
    const m = S.matches.find((x) => x.id === c.match_id);
    const d = {
      id: c.id, nome: c.nome, match_id: c.match_id, gerenciador: ORG[c.gerenciador], membros: [mesmaOrg, m.outra.orgao], criado_em: c.criado_em, data_fim_contrato: c.data_fim_contrato || null,
      ocorrencias_abertas: S.ocorrencias.filter((o) => o.comite_id === c.id && o.status !== 'resolvida').length,
    };
    if (completo) {
      d.tarefas = c.tarefas.map((t) => ({ id: t.id, comite_id: c.id, ordem: t.ordem, titulo: t.titulo, responsavel_orgao_id: t.resp, prazo: t.prazo, concluida: t.concluida }));
      d.mensagens = clone(c.mensagens);
      d.match = verMatch(S, m);
    }
    return d;
  };
  const primeiroDia = (ano, mes, desl) => { const t = ano * 12 + (mes - 1) + desl; return `${Math.floor(t / 12)}-${String((t % 12) + 1).padStart(2, '0')}-01`; };

  function criarComite(S, m) {
    const mi = S.demandas.find((d) => d.id === m.minha_id);
    const ger = ORG[m.caminho.gerenciador];
    const mes = Math.min(mi.mes_previsto, m.outra.mes_previsto);
    const passos = m.caminho.modelo === 'capacitacao_compartilhada'
      ? [['Definir conteúdo, formato e número de vagas', null, -2], ['Formalizar no acordo de cooperação técnica', ger.id, -1], ['Realizar a capacitação compartilhada', ger.id, 0]]
      : [['Alinhar especificação técnica e critérios sustentáveis', null, -3], ['Elaborar ETP e termo de referência conjuntos', ger.id, -2], ['Publicar a IRP (prazo mínimo de 8 dias úteis)', ger.id, -1], ['Realizar a licitação', ger.id, 0], ['Assinar a ata e emitir o contrato de cada órgão', null, 1]];
    const id = S.prox.comite++;
    S.comites.push({ id, match_id: m.id, nome: `Comitê de cooperação — ${mi.descricao}`, gerenciador: ger.sigla, criado_em: new Date().toISOString(),
      tarefas: passos.map(([titulo, resp, desl], i) => ({ id: S.prox.tarefa++, ordem: i + 1, titulo, resp, prazo: primeiroDia(mi.ano, mes, desl), concluida: false })), mensagens: [] });
    return id;
  }

  /* Incentivos: mesma regra da API (100 pontos por match conectado + 1 por R$ 1.000 de economia, bônus máx. 100). */
  const pontosDoMatch = (m) => 100 + Math.min(Math.floor((m.economia_valor || 0) / 1000), 100);
  const BASE_PONTOS = { 'TRT 13': 0, JFPB: 180, TJPB: 120, 'TRE-RN': 90 }; // pontos fictícios de outras conexões da rede
  const pontosMeus = (S) => S.matches.filter((m) => m.status === 'conectado').reduce((a, m) => a + pontosDoMatch(m), 0);
  function incentivos(S) {
    const conect = S.matches.filter((m) => m.status === 'conectado');
    const tot = { 'TRE-PB': pontosMeus(S), ...BASE_PONTOS };
    conect.forEach((m) => { tot[m.outra.orgao.sigla] = (tot[m.outra.orgao.sigla] || 0) + pontosDoMatch(m); });
    const qtd = (sig) => conect.filter((m) => sig === 'TRE-PB' || m.outra.orgao.sigla === sig).length;
    const ranking = Object.keys(ORG).map((sig) => ({ orgao_id: ORG[sig].id, sigla: sig, nome: ORG[sig].nome, pontos: tot[sig] || 0, matches: qtd(sig), meu: sig === 'TRE-PB' }))
      .sort((a, b) => b.pontos - a.pontos || a.sigla.localeCompare(b.sigla)).map((r, i) => ({ ...r, posicao: i + 1 }));
    const historico = conect.map((m) => ({ match_id: m.id, pontos: pontosDoMatch(m), motivo: 'Match conectado' + ((m.economia_valor || 0) >= 1000 ? ` + bônus de economia (${Math.min(Math.floor(m.economia_valor / 1000), 100)})` : ''), criado_em: m.atualizado_em }));
    return { meus_pontos: pontosMeus(S), posicao: ranking.find((r) => r.meu).posicao, ranking, historico, regras: { base: 100, por_mil_reais: 1, bonus_maximo: 100 } };
  }

  const indicadores = (S) => {
    const ms = S.matches;
    const conectados = ms.filter((m) => m.status === 'conectado');
    return { demandas: S.demandas.length, matches_sugeridos: ms.filter((m) => m.status === 'sugerido').length, matches_conectados: conectados.length,
      matches_recusados: ms.filter((m) => m.status === 'recusado').length, processos_evitados: conectados.length,
      economia_estimada_conectados: conectados.reduce((a, m) => a + (m.economia_valor || 0), 0), pontos: pontosMeus(S) };
  };

  function chamar(metodo, caminho, corpo) {
    return new Promise((resolve, reject) => {
      try { resolve(clone(rotear(metodo, caminho, corpo))); } catch (e) { reject(e); }
    });
  }

  function rotear(metodo, caminho, corpo) {
    const [path, qs] = caminho.split('?');
    const q = new URLSearchParams(qs || '');
    const S = ler();
    let r;
    if (metodo === 'POST' && path === '/api/auth/logout') return { ok: true };
    const usuario = (GM.sessao() || {}).usuario || {}, orgaoSessao = (GM.sessao() || {}).orgao || {};
    const fiscal = usuario.perfil === 'fiscal';
    if (fiscal && !FISCAL_OK.some(([m, re]) => m === metodo && re.test(path))) throw erro(403, 'O perfil de fiscalização só acessa comitês e ocorrências.');
    const verOc = (o) => {
      const c = S.comites.find((x) => x.id === o.comite_id), t = c && c.tarefas.find((x) => x.id === o.tarefa_id);
      return { ...o, comite_nome: c ? c.nome : null, tarefa_titulo: t ? t.titulo : null, tarefa_ordem: t ? t.ordem : null, respostas: o.respostas.map((x) => ({ ...x })) };
    };
    if (metodo === 'GET' && path === '/api/ocorrencias') {
      let l = S.ocorrencias;
      if (q.get('comite_id')) l = l.filter((o) => o.comite_id === +q.get('comite_id'));
      if (q.get('status')) l = l.filter((o) => o.status === q.get('status'));
      return { ocorrencias: [...l].reverse().map(verOc) };
    }
    if ((r = path.match(/^\/api\/comites\/(\d+)\/ocorrencias$/)) && metodo === 'POST') {
      if (!fiscal) throw erro(403, 'Somente o perfil de fiscalização pode fazer isso.');
      const c = S.comites.find((x) => x.id === +r[1]);
      if (!c) throw erro(404, 'Comitê não encontrado.');
      const b = corpo || {}, desc = String(b.descricao || '').trim(), grav = String(b.gravidade || 'media');
      if (!OC_TIPOS.includes(b.tipo)) throw erro(422, "'tipo' deve ser: " + [...OC_TIPOS].sort().join(', ') + '.');
      if (!['baixa', 'media', 'alta'].includes(grav)) throw erro(422, "'gravidade' deve ser: baixa, media ou alta.");
      if (desc.length < 10) throw erro(422, 'Descreva a ocorrência com pelo menos 10 caracteres.');
      let tid = null;
      if (b.tarefa_id !== null && b.tarefa_id !== undefined && b.tarefa_id !== '') {
        if (!c.tarefas.some((t) => t.id === +b.tarefa_id)) throw erro(422, "'tarefa_id' não pertence a este comitê.");
        tid = +b.tarefa_id;
      }
      const o = { id: S.prox.ocorrencia++, comite_id: c.id, tarefa_id: tid, tipo: b.tipo, gravidade: grav, descricao: desc, status: 'aberta', autor: usuario.nome, criada_em: new Date().toISOString(), resolvida_em: null, respostas: [] };
      S.ocorrencias.push(o); gravar(S);
      return { ocorrencia: verOc(o) };
    }
    if ((r = path.match(/^\/api\/ocorrencias\/(\d+)\/respostas$/)) && metodo === 'POST') {
      const o = S.ocorrencias.find((x) => x.id === +r[1]);
      if (!o) throw erro(404, 'Ocorrência não encontrada.');
      const texto = String((corpo || {}).texto || '').trim();
      if (!texto) throw erro(422, 'A resposta não pode ser vazia.');
      if (o.status === 'resolvida' && !fiscal) throw erro(409, 'Esta ocorrência já foi resolvida pela fiscalização.');
      o.respostas.push({ id: S.prox.resposta++, texto, autor: usuario.nome, perfil: usuario.perfil, orgao: orgaoSessao.sigla, criada_em: new Date().toISOString() });
      if (!fiscal && o.status === 'aberta') o.status = 'respondida';
      gravar(S);
      return { ocorrencia: verOc(o) };
    }
    if ((r = path.match(/^\/api\/ocorrencias\/(\d+)$/)) && metodo === 'PATCH') {
      if (!fiscal) throw erro(403, 'Somente o perfil de fiscalização pode fazer isso.');
      const o = S.ocorrencias.find((x) => x.id === +r[1]);
      if (!o) throw erro(404, 'Ocorrência não encontrada.');
      const st = String((corpo || {}).status || '');
      if (!['aberta', 'resolvida'].includes(st)) throw erro(422, "'status' deve ser 'resolvida' (encerrar) ou 'aberta' (reabrir).");
      o.status = st; o.resolvida_em = st === 'resolvida' ? new Date().toISOString() : null;
      gravar(S);
      return { ocorrencia: verOc(o) };
    }
    if (metodo === 'GET' && path === '/api/painel') {
      const meu = indicadores(S);
      return { rede: { ...meu, demandas: 14, matches_sugeridos: meu.matches_sugeridos + 3, matches_conectados: meu.matches_conectados + 1, processos_evitados: meu.processos_evitados + 1, orgaos_cooperados: 5, economia_estimada_conectados: meu.economia_estimada_conectados + 143500, pontos: meu.pontos + 390 }, meu_orgao: meu,
        observacao: 'Economia estimada com parâmetros ilustrativos; não considera valores sigilosos.' };
    }
    if (metodo === 'GET' && path === '/api/incentivos') return incentivos(S);
    if (path === '/api/demandas') {
      if (metodo === 'GET') {
        let l = S.demandas.filter((d) => (!q.get('ano') || d.ano === +q.get('ano')) && (!q.get('natureza') || d.natureza === q.get('natureza')));
        return { demandas: l.map(verDemanda) };
      }
      if (metodo === 'POST') {
        const d = dadosDemanda(corpo);
        d.id = S.prox.demanda++; d.orgao = mesmaOrg; d.origem = 'manual';
        S.demandas.push(d); gravar(S);
        return { demanda: d, matches: { criados: 0, atualizados: 0, removidos: 0 }, demo: true };
      }
    }
    if (path === '/api/demandas/importar') throw erro(400, 'A importação de CSV só funciona conectado à API real.');
    if ((r = path.match(/^\/api\/demandas\/(\d+)$/))) {
      const i = S.demandas.findIndex((d) => d.id === +r[1]);
      if (i < 0) throw erro(404, 'Demanda não encontrada.');
      if (metodo === 'GET') return { demanda: verDemanda(S.demandas[i]) };
      if (metodo === 'PUT') { const novo = dadosDemanda({ ...S.demandas[i], ...corpo }); S.demandas[i] = { ...S.demandas[i], ...novo }; gravar(S); return { demanda: S.demandas[i], matches: { criados: 0, atualizados: 0, removidos: 0 }, demo: true }; }
      if (metodo === 'DELETE') {
        if (S.matches.some((m) => m.minha_id === +r[1] && m.status === 'conectado')) throw erro(409, 'Esta demanda já tem um comitê de cooperação ativo e não pode ser excluída.');
        S.demandas.splice(i, 1); S.matches = S.matches.filter((m) => m.minha_id !== +r[1]); gravar(S); return { ok: true };
      }
    }
    if (metodo === 'POST' && path === '/api/matches/gerar') return { matches: { criados: 0, atualizados: 0, removidos: 0 } };
    if (metodo === 'GET' && path === '/api/matches') {
      let l = S.matches.filter((m) => S.demandas.some((d) => d.id === m.minha_id));
      if (q.get('status')) l = l.filter((m) => m.status === q.get('status'));
      if (['1', 'true', 'sim'].includes(q.get('pendentes'))) l = l.filter((m) => m.status === 'sugerido' && !m.minha_decisao);
      l.sort((a, b) => b.score - a.score || a.id - b.id);
      return { matches: l.map((m) => verMatch(S, m)), total: l.length, aviso: 'Sugestões geradas automaticamente para apoiar a decisão. A decisão de cooperar é sempre dos gestores.' };
    }
    if ((r = path.match(/^\/api\/matches\/(\d+)$/)) && metodo === 'GET') {
      const m = S.matches.find((x) => x.id === +r[1]);
      if (!m) throw erro(404, 'Match não encontrado.');
      return { match: verMatch(S, m), aviso: 'Sugestões geradas automaticamente para apoiar a decisão. A decisão de cooperar é sempre dos gestores.' };
    }
    if ((r = path.match(/^\/api\/matches\/(\d+)\/decisao$/)) && metodo === 'POST') {
      const m = S.matches.find((x) => x.id === +r[1]);
      if (!m) throw erro(404, 'Match não encontrado.');
      const dec = String((corpo || {}).decisao || '');
      if (!['conectar', 'recusar'].includes(dec)) throw erro(422, "'decisao' deve ser 'conectar' ou 'recusar'.");
      if (m.status !== 'sugerido') throw erro(409, `Este match já está '${m.status}'.`);
      m.minha_decisao = dec; let deu = false;
      if (dec === 'recusar') m.status = 'recusado';
      else if (m.outro_conectou) { m.status = 'conectado'; m.comite_id = criarComite(S, m); deu = true; }
      gravar(S);
      return { deu_match: deu, match: verMatch(S, m), ...(deu ? { pontos_ganhos: pontosDoMatch(m) } : {}) };
    }
    if (metodo === 'GET' && path === '/api/comites') return { comites: S.comites.map((c) => verComite(S, c, false)) };
    if ((r = path.match(/^\/api\/comites\/(\d+)$/)) && metodo === 'PATCH') {
      const c = S.comites.find((x) => x.id === +r[1]);
      if (!c) throw erro(404, 'Comitê não encontrado.');
      if (!corpo || !('data_fim_contrato' in corpo)) throw erro(422, "Informe 'data_fim_contrato' (AAAA-MM-DD) ou null para limpar.");
      const fim = corpo.data_fim_contrato || null;
      if (fim && !/^\d{4}-\d{2}-\d{2}$/.test(fim)) throw erro(422, "'data_fim_contrato' deve estar no formato AAAA-MM-DD.");
      c.data_fim_contrato = fim; gravar(S);
      return { comite: verComite(S, c, false) };
    }
    if ((r = path.match(/^\/api\/comites\/(\d+)$/)) && metodo === 'GET') {
      const c = S.comites.find((x) => x.id === +r[1]);
      if (!c) throw erro(404, 'Comitê não encontrado.');
      return { comite: verComite(S, c, true) };
    }
    if ((r = path.match(/^\/api\/comites\/(\d+)\/mensagens$/)) && metodo === 'POST') {
      const c = S.comites.find((x) => x.id === +r[1]);
      if (!c) throw erro(404, 'Comitê não encontrado.');
      const texto = String((corpo || {}).texto || '').trim();
      if (!texto) throw erro(422, 'A mensagem não pode ser vazia.');
      c.mensagens.push({ id: S.prox.msg++, texto, autor: GM.sessao().usuario.nome, orgao: 'TRE-PB', enviada_em: new Date().toISOString() });
      gravar(S);
      return { mensagem: { id: 0, texto, autor: GM.sessao().usuario.nome } };
    }
    if ((r = path.match(/^\/api\/comites\/(\d+)\/tarefas\/(\d+)$/)) && metodo === 'PATCH') {
      const c = S.comites.find((x) => x.id === +r[1]);
      const t = c && c.tarefas.find((x) => x.id === +r[2]);
      if (!t) throw erro(404, 'Tarefa não encontrada.');
      t.concluida = !!(corpo || {}).concluida;
      if ((corpo || {}).prazo) t.prazo = corpo.prazo;
      gravar(S);
      return { tarefa: { ...t, comite_id: c.id, responsavel_orgao_id: t.resp, concluida: t.concluida ? 1 : 0 } };
    }
    throw erro(404, 'Rota não encontrada (modo demonstração).');
  }

  function dadosDemanda(b) {
    const d = { ...b };
    if (!String(d.descricao || '').trim()) throw erro(422, "O campo 'descricao' é obrigatório.");
    d.descricao = String(d.descricao).trim();
    ['ano', 'mes_previsto', 'quantidade'].forEach((k) => { d[k] = Number(d[k]); });
    d.valor_estimado = d.valor_estimado === '' || d.valor_estimado == null ? null : Number(d.valor_estimado);
    d.valor_sigiloso = !!d.valor_sigiloso;
    d.criterios_sustentaveis = d.criterios_sustentaveis || [];
    return d;
  }

  // iniciar: mantém o que já foi cadastrado no navegador (só cria os dados na 1ª vez).
  function iniciar() { ler(); }
  // reiniciar: volta aos dados originais da demonstração (apaga demandas, conexões e mensagens criadas aqui).
  function reiniciar() { gravar(inicial()); try { localStorage.removeItem('gm_alertas_d_1'); } catch { /* ignora */ } }
  return { chamar, iniciar, reiniciar, ORG, FISCAL: FISCAL_ORG };
})();
GM.Demo = Demo;
