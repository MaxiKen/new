/* =====================================================================
   Admin Studio — site settings, structure and the smaller collections
   (admin only)
   ===================================================================== */

/* =====================================================================
   SETTINGS
   ===================================================================== */
Pages.settings = async function (params, el) {
  const s = await A.get('settings') || {};
  const site = s.site || {}, th = s.themes || {}, seo = s.seo || {},
        social = s.social || {}, footer = s.footer || {}, contact = s.contact || {};
  const lt = th.light || {}, dk = th.dark || {};
  const colors = [['primary', 'Primary'], ['secondary', 'Secondary'], ['accent', 'Accent'],
                  ['background', 'Background'], ['surface', 'Surface'], ['text', 'Text'],
                  ['text_secondary', 'Muted text'], ['border', 'Borders']];

  el.innerHTML = `
    <div class="page-head">
      <div><h1>Settings</h1><p>Everything visitors see: name, colours, links and SEO.</p></div>
      <div class="head-actions"><button class="btn btn-p" data-act="settings:save">Save settings</button></div>
    </div>

    <div class="grid g2">
      <div class="card">
        <div class="card-hd"><h2>Site identity</h2></div>
        <div class="row">
          <div class="fg"><label>Site name <span class="req">*</span></label>
            <input class="fc" id="st-name" value="${attr(site.name || '')}"></div>
          <div class="fg"><label>Tagline</label><input class="fc" id="st-tag" value="${attr(site.tagline || '')}"></div>
        </div>
        <div class="fg"><label>Description</label>
          <textarea class="fc" id="st-desc">${esc(site.description || '')}</textarea></div>
        ${Upload.field('logo', { label: 'Logo', bucket: 'site-assets', value: site.logo })}
        ${Upload.field('favicon', { label: 'Favicon', bucket: 'site-assets', value: site.favicon, accept: 'image/*' })}
      </div>

      <div class="card">
        <div class="card-hd"><h2>Home hero</h2></div>
        <div class="fg"><label>Headline</label><input class="fc" id="st-ht" value="${attr(site.hero_title || '')}"></div>
        <div class="fg"><label>Sub-headline</label><input class="fc" id="st-hs" value="${attr(site.hero_subtitle || '')}"></div>
        ${Upload.field('hero', { label: 'Background image', bucket: 'site-assets', value: site.hero_image, hint: 'Wide image, at least 1600px' })}
      </div>
    </div>

    <div class="card">
      <div class="card-hd"><h2>Theme colours</h2>
        <p class="muted">Applied instantly on the public site.</p></div>
      <h3 style="font-size:.8rem;margin:6px 0 10px">Light theme</h3>
      <div class="color-grid">
        ${colors.map(([k, l]) => `<div><label>${l}</label>
          <input type="color" id="cl-${k}" value="${attr(lt[k] || '#3b82f6')}"></div>`).join('')}
      </div>
      <div class="sep"></div>
      <h3 style="font-size:.8rem;margin:6px 0 10px">Dark theme</h3>
      <div class="color-grid">
        ${colors.map(([k, l]) => `<div><label>${l}</label>
          <input type="color" id="cd-${k}" value="${attr(dk[k] || '#111827')}"></div>`).join('')}
      </div>
    </div>

    <div class="grid g2">
      <div class="card">
        <div class="card-hd"><h2>Social profiles</h2></div>
        ${['twitter', 'facebook', 'linkedin', 'instagram', 'youtube'].map(k => `
          <div class="fg"><label>${k[0].toUpperCase() + k.slice(1)}</label>
            <input class="fc" id="so-${k}" value="${attr(social[k] || '')}" placeholder="https://"></div>`).join('')}
      </div>

      <div>
        <div class="card">
          <div class="card-hd"><h2>Search engines</h2></div>
          <div class="fg"><label>Meta title</label><input class="fc" id="se-t" value="${attr(seo.title || '')}"></div>
          <div class="fg"><label>Meta description</label>
            <textarea class="fc" id="se-d" style="min-height:60px">${esc(seo.description || '')}</textarea></div>
          <div class="fg"><label>Keywords</label><input class="fc" id="se-k" value="${attr(seo.keywords || '')}"></div>
        </div>
        <div class="card">
          <div class="card-hd"><h2>Contact &amp; footer</h2></div>
          <div class="fg"><label>Contact email</label><input class="fc" id="ct-mail" value="${attr(contact.email || '')}"></div>
          <div class="fg"><label>Web3Forms key <span class="muted">(optional email relay)</span></label>
            <input class="fc" id="ct-key" value="${attr(contact.web3forms_key || '')}"></div>
          <div class="fg"><label>Copyright line</label><input class="fc" id="ft-copy" value="${attr(footer.copyright || '')}"></div>
        </div>
      </div>
    </div>`;
};

A.on('settings:save', async () => {
  const colors = ['primary', 'secondary', 'accent', 'background', 'surface', 'text', 'text_secondary', 'border'];
  const pick = (p) => colors.reduce((o, k) => (o[k] = val(p + k), o), {});
  const r = await A.act('api_save_settings', {
    p_data: {
      site: {
        name: val('st-name'), tagline: val('st-tag'), description: val('st-desc'),
        logo: Upload.value('logo'), favicon: Upload.value('favicon'),
        hero_image: Upload.value('hero'), hero_title: val('st-ht'), hero_subtitle: val('st-hs')
      },
      themes: { light: pick('cl-'), dark: pick('cd-') },
      seo: { title: val('se-t'), description: val('se-d'), keywords: val('se-k') },
      social: ['twitter', 'facebook', 'linkedin', 'instagram', 'youtube']
        .reduce((o, k) => (o[k] = val('so-' + k), o), {}),
      footer: { copyright: val('ft-copy'), links: [] },
      contact: { email: val('ct-mail'), web3forms_key: val('ct-key') }
    }
  }, 'Settings saved');
  if (r) toast('Saved — reload the site to see the changes', 'ok');
});

/* =====================================================================
   CATEGORIES & SUBTOPICS
   ===================================================================== */
Pages.categories = async function (params, el) {
  await A.refreshTaxonomy();
  const cats = [...(A.cache.categories || [])].sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0));
  const subs = A.cache.subtopics || [];

  el.innerHTML = `
    <div class="page-head">
      <div><h1>Categories &amp; subtopics</h1>
        <p>The menu of your site. Authors can file posts under any of these.</p></div>
      <div class="head-actions"><button class="btn btn-p" data-act="cat:new">＋ New category</button></div>
    </div>

    ${cats.map((c, i) => {
      const kids = subs.filter(s => s.category_id === c.id)
        .sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0));
      const special = ['downloads', 'glossary', 'faqs', 'about'].includes(c.type);
      return `<div class="card">
        <div class="card-hd">
          <div>
            <h2>${esc(c.title)}
              ${c.hidden ? '<span class="pill p-err">hidden</span>' : '<span class="pill p-ok">visible</span>'}
              ${c.system_locked ? '<span class="pill p-mute">built-in</span>' : ''}</h2>
            <p class="muted">/${esc(c.id)}${c.description ? ' · ' + esc(c.description) : ''}</p>
          </div>
          <div class="t-actions">
            <button class="btn btn-o btn-s" data-act="cat:move" data-id="${attr(c.id)}" data-dir="-1" ${i === 0 ? 'disabled' : ''}>↑</button>
            <button class="btn btn-o btn-s" data-act="cat:move" data-id="${attr(c.id)}" data-dir="1" ${i === cats.length - 1 ? 'disabled' : ''}>↓</button>
            <button class="btn btn-o btn-s" data-act="cat:hide" data-id="${attr(c.id)}" data-hidden="${c.hidden ? '' : '1'}">
              ${c.hidden ? 'Show' : 'Hide'}</button>
            ${c.system_locked ? '' : `<button class="btn btn-o btn-s" data-act="cat:edit" data-id="${attr(c.id)}">Edit</button>
              <button class="btn btn-d btn-s" data-act="cat:del" data-id="${attr(c.id)}">Delete</button>`}
          </div>
        </div>
        ${special ? `<p class="muted" style="font-size:.8rem">This is a built-in page managed from its own screen.</p>` : `
          ${kids.length ? kids.map((s, j) => `
            <div class="list-item">
              <div class="li-main"><div class="t-title">${esc(s.title)}
                  ${s.hidden ? '<span class="pill p-err">hidden</span>' : ''}
                  ${s.system_locked ? '<span class="pill p-mute">built-in</span>' : ''}</div>
                <div class="t-sub">/${esc(s.id)}${s.description ? ' · ' + esc(s.description) : ''}</div></div>
              <button class="btn btn-o btn-s" data-act="sub:move" data-id="${attr(s.id)}" data-dir="-1" ${j === 0 ? 'disabled' : ''}>↑</button>
              <button class="btn btn-o btn-s" data-act="sub:move" data-id="${attr(s.id)}" data-dir="1" ${j === kids.length - 1 ? 'disabled' : ''}>↓</button>
              <button class="btn btn-o btn-s" data-act="sub:hide" data-id="${attr(s.id)}" data-hidden="${s.hidden ? '' : '1'}">${s.hidden ? 'Show' : 'Hide'}</button>
              ${s.system_locked ? '' : `<button class="btn btn-o btn-s" data-act="sub:edit" data-id="${attr(s.id)}">Edit</button>
                <button class="btn btn-d btn-s" data-act="sub:del" data-id="${attr(s.id)}">Del</button>`}
            </div>`).join('') : '<p class="muted" style="font-size:.82rem">No subtopics yet.</p>'}
          <button class="btn btn-o btn-s" style="margin-top:12px" data-act="sub:new" data-cat="${attr(c.id)}">＋ Add subtopic</button>`}
      </div>`;
    }).join('')}`;
};

function taxonomyDialog({ kind, item, catId }) {
  const isNew = !item;
  openModal(`<h2>${isNew ? 'New' : 'Edit'} ${kind === 'category' ? 'category' : 'subtopic'}</h2>
    <div class="fg" style="margin-top:14px"><label>Title <span class="req">*</span></label>
      <input class="fc" id="tx-title" autofocus value="${attr(item?.title || '')}"></div>
    <div class="fg"><label>URL id</label>
      <input class="fc" id="tx-id" value="${attr(item?.id || '')}" ${isNew ? '' : 'readonly'}></div>
    ${kind === 'category' ? `<div class="fg"><label>Icon</label>
      <input class="fc" id="tx-icon" value="${attr(item?.icon || 'edit')}"
        placeholder="edit, download, book, help, info, briefcase"></div>` : ''}
    <div class="fg"><label>Description</label>
      <input class="fc" id="tx-desc" value="${attr(item?.description || '')}"></div>
    <div class="m-act"><button class="btn btn-o" data-act="modal:close">Cancel</button>
      <button class="btn btn-p" data-act="tax:save" data-kind="${kind}" data-cat="${attr(catId || item?.category_id || '')}">Save</button></div>`,
    { small: true });
  if (isNew) document.getElementById('tx-title').addEventListener('input', (e) => {
    if (!document.getElementById('tx-id').dataset.t) setVal('tx-id', slugify(e.target.value));
  });
  document.getElementById('tx-id').addEventListener('input', (e) => { e.target.dataset.t = '1'; });
}

A.on('cat:new', () => taxonomyDialog({ kind: 'category' }));
A.on('cat:edit', (d) => taxonomyDialog({ kind: 'category', item: A.cache.categories.find(c => c.id === d.id) }));
A.on('sub:new', (d) => taxonomyDialog({ kind: 'subtopic', catId: d.cat }));
A.on('sub:edit', (d) => taxonomyDialog({ kind: 'subtopic', item: A.cache.subtopics.find(s => s.id === d.id) }));

A.on('tax:save', async (d) => {
  const data = {
    id: val('tx-id'), title: val('tx-title'), description: val('tx-desc'),
    icon: val('tx-icon') || 'edit'
  };
  if (d.kind === 'subtopic') data.category_id = d.cat;
  const r = await A.act('api_save_taxonomy', { p_kind: d.kind, p_data: data });
  if (r) { closeModal(); A.go('categories'); }
});

['cat', 'sub'].forEach(pfx => {
  const kind = pfx === 'cat' ? 'category' : 'subtopic';
  A.on(pfx + ':hide', async (d) => {
    await A.act('api_taxonomy_action', { p_kind: kind, p_id: d.id, p_action: 'hide', p_value: { hidden: !!d.hidden } }, false);
    A.go('categories');
  });
  A.on(pfx + ':move', async (d) => {
    await A.act('api_taxonomy_action', { p_kind: kind, p_id: d.id, p_action: 'move', p_value: { dir: Number(d.dir) } }, false);
    A.go('categories');
  });
  A.on(pfx + ':del', async (d) => {
    const ok = await confirmDialog({
      title: `Delete this ${kind}?`, danger: true, okLabel: 'Delete',
      body: kind === 'category'
        ? '<p>Its subtopics are deleted as well. Posts inside it stay, but lose their place in the menu.</p>'
        : '<p>Posts filed under it stay online.</p>'
    });
    if (!ok) return;
    await A.act('api_taxonomy_action', { p_kind: kind, p_id: d.id, p_action: 'delete' });
    A.go('categories');
  });
});

/* =====================================================================
   MEDIA LIBRARY
   ===================================================================== */
Pages.media = async function (params, el) {
  const items = await A.list('media');
  el.innerHTML = `
    <div class="page-head">
      <div><h1>Media</h1><p>${items.length} file${items.length === 1 ? '' : 's'} uploaded${A.isAdmin ? '' : ' by you'}.</p></div>
      <div class="head-actions">
        <button class="btn btn-p" data-act="upload:pick" data-id="lib">⬆ Upload</button>
      </div>
    </div>
    <div style="display:none">${Upload.field('lib', { label: '', bucket: 'post-images', value: '' })}</div>
    <div class="card">
      ${items.length ? `<div class="media-grid">
        ${items.map(m => `<div class="media-item">
          <div class="thumb">${/^image\//.test(m.mime || '')
            ? `<img src="${attr(m.url)}" alt="" loading="lazy">`
            : `<span style="font-size:1.6rem">📄</span>`}</div>
          <div class="mi-foot">
            <span title="${attr(m.filename || '')}" style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">
              ${esc(m.filename || 'file')}</span>
            <span class="nowrap">${fmtBytes(m.size_bytes)}</span>
          </div>
          <div class="mi-foot" style="border-top:1px solid var(--line)">
            <button class="btn btn-ghost btn-s" data-act="media:copy" data-url="${attr(m.url)}">Copy URL</button>
            <button class="btn btn-ghost btn-s" data-act="media:del" data-id="${attr(m.id)}">Delete</button>
          </div>
        </div>`).join('')}
      </div>` : '<p class="muted">Nothing uploaded yet. Images you add inside posts show up here too.</p>'}
    </div>`;
};
A.on('media:copy', (d) => {
  navigator.clipboard?.writeText(d.url).then(() => toast('URL copied', 'ok'), () => toast(d.url, 'info'));
});
A.on('media:del', async (d) => {
  const ok = await confirmDialog({ title: 'Remove from the library?', danger: true, okLabel: 'Remove',
    body: '<p>The file itself stays in storage, but it disappears from this list.</p>' });
  if (!ok) return;
  await A.act('api_delete_entry', { p_entity: 'media', p_id: d.id });
  A.go('media');
});

/* =====================================================================
   DOWNLOADS
   ===================================================================== */
Pages.downloads = async function (params, el) {
  const rows = await A.list('downloads');
  el.innerHTML = `
    <div class="page-head">
      <div><h1>Downloads</h1><p>Files readers can grab from the downloads page.</p></div>
      <div class="head-actions"><button class="btn btn-p" data-act="dl:new">＋ New download</button></div>
    </div>
    <div class="card pad0"><div class="t-wrap"><table>
      <thead><tr><th>Name</th><th>Format</th><th>Size</th><th>Status</th><th></th></tr></thead>
      <tbody>${rows.length ? rows.map(d => `<tr>
        <td><div class="t-title">${esc(d.name)}</div><div class="t-sub">${esc(d.description || '')}</div></td>
        <td class="t-sub">${esc(d.file_format || '—')}</td>
        <td class="t-sub">${esc(d.file_size || '—')}</td>
        <td>${d.is_published ? '<span class="pill p-ok">visible</span>' : '<span class="pill p-mute">hidden</span>'}</td>
        <td><div class="t-actions">
          <button class="btn btn-o btn-s" data-act="dl:edit" data-id="${attr(d.id)}">Edit</button>
          <button class="btn btn-o btn-s" data-act="dl:pub" data-id="${attr(d.id)}" data-v="${d.is_published ? '' : '1'}">
            ${d.is_published ? 'Hide' : 'Show'}</button>
          ${d.system_locked ? '' : `<button class="btn btn-d btn-s" data-act="dl:del" data-id="${attr(d.id)}">Del</button>`}
        </div></td></tr>`).join('') : emptyRow(5, 'No downloads yet.')}</tbody>
    </table></div></div>`;
};
A.on('dl:new', () => downloadDialog(null));
A.on('dl:edit', async (d) => downloadDialog(await A.get('download', d.id)));
A.on('dl:pub', async (d) => {
  await A.act('api_entry_action', { p_entity: 'download', p_id: d.id, p_action: 'publish', p_value: { value: !!d.v } }, false);
  A.go('downloads');
});
A.on('dl:del', async (d) => {
  if (!await confirmDialog({ title: 'Delete this download?', danger: true, okLabel: 'Delete' })) return;
  await A.act('api_delete_entry', { p_entity: 'download', p_id: d.id });
  A.go('downloads');
});
function downloadDialog(d) {
  d = d || {};
  openModal(`<h2>${d.id ? 'Edit' : 'New'} download</h2>
    <div class="row" style="margin-top:14px">
      <div class="fg"><label>Name <span class="req">*</span></label><input class="fc" id="dl-name" autofocus value="${attr(d.name || '')}"></div>
      <div class="fg"><label>Id</label><input class="fc" id="dl-id" value="${attr(d.id || '')}" ${d.id ? 'readonly' : ''}></div>
    </div>
    <div class="fg"><label>Description</label><textarea class="fc" id="dl-desc">${esc(d.description || '')}</textarea></div>
    ${Upload.field('dlfile', { label: 'File', bucket: 'download-files', value: d.file_url, accept: '*/*' })}
    <div class="row">
      <div class="fg"><label>Format</label><input class="fc" id="dl-fmt" value="${attr(d.file_format || '')}" placeholder="pdf"></div>
      <div class="fg"><label>Size label</label><input class="fc" id="dl-size" value="${attr(d.file_size || '')}" placeholder="2.4 MB"></div>
    </div>
    ${Upload.field('dlthumb', { label: 'Thumbnail', bucket: 'download-files', value: d.thumbnail })}
    <div class="fg"><label>Tags</label><input class="fc" id="dl-tags" value="${attr((d.tags || []).join(', '))}"></div>
    <div class="m-act"><button class="btn btn-o" data-act="modal:close">Cancel</button>
      <button class="btn btn-p" data-act="dl:save">Save</button></div>`, {});
  if (!d.id) document.getElementById('dl-name').addEventListener('input', e => setVal('dl-id', slugify(e.target.value)));
}
A.on('dl:save', async () => {
  const r = await A.act('api_save_entry', {
    p_entity: 'download',
    p_data: {
      id: val('dl-id') || slugify(val('dl-name')), name: val('dl-name'), description: val('dl-desc'),
      file_url: Upload.value('dlfile'), file_format: val('dl-fmt'), file_size: val('dl-size'),
      thumbnail: Upload.value('dlthumb'), tags: val('dl-tags').split(',').map(t => t.trim()).filter(Boolean),
      is_published: true
    }
  });
  if (r) { closeModal(); A.go('downloads'); }
});

/* =====================================================================
   GLOSSARY
   ===================================================================== */
Pages.glossary = async function (params, el) {
  const rows = await A.list('glossary');
  el.innerHTML = `
    <div class="page-head">
      <div><h1>Glossary</h1><p>${rows.length} term${rows.length === 1 ? '' : 's'}.</p></div>
      <div class="head-actions"><button class="btn btn-p" data-act="gl:new">＋ New term</button></div>
    </div>
    <div class="card pad0"><div class="t-wrap"><table>
      <thead><tr><th>Word</th><th>Definition</th><th></th></tr></thead>
      <tbody>${rows.length ? rows.map(g => `<tr>
        <td class="t-title">${esc(g.word)}</td>
        <td class="t-sub">${esc((g.definition || '').slice(0, 160))}${(g.definition || '').length > 160 ? '…' : ''}</td>
        <td><div class="t-actions">
          <button class="btn btn-o btn-s" data-act="gl:edit" data-id="${g.id}">Edit</button>
          ${g.system_locked ? '' : `<button class="btn btn-d btn-s" data-act="gl:del" data-id="${g.id}">Del</button>`}
        </div></td></tr>`).join('') : emptyRow(3, 'No terms yet.')}</tbody>
    </table></div></div>`;
};
A.on('gl:new', () => glossaryDialog(null));
A.on('gl:edit', async (d) => glossaryDialog(await A.get('glossary', d.id)));
A.on('gl:del', async (d) => {
  if (!await confirmDialog({ title: 'Delete this term?', danger: true, okLabel: 'Delete' })) return;
  await A.act('api_delete_entry', { p_entity: 'glossary', p_id: d.id });
  A.go('glossary');
});
function glossaryDialog(g) {
  g = g || {};
  openModal(`<h2>${g.id ? 'Edit' : 'New'} term</h2>
    <div class="fg" style="margin-top:14px"><label>Word <span class="req">*</span></label>
      <input class="fc" id="gl-word" autofocus value="${attr(g.word || '')}"></div>
    <div class="fg"><label>Definition <span class="req">*</span></label>
      <textarea class="fc" id="gl-def" style="min-height:120px">${esc(g.definition || '')}</textarea></div>
    <div class="m-act"><button class="btn btn-o" data-act="modal:close">Cancel</button>
      <button class="btn btn-p" data-act="gl:save" data-id="${g.id || ''}">Save</button></div>`, { small: true });
}
A.on('gl:save', async (d) => {
  const r = await A.act('api_save_entry', {
    p_entity: 'glossary', p_data: { id: d.id || null, word: val('gl-word'), definition: val('gl-def') }
  });
  if (r) { closeModal(); A.go('glossary'); }
});

/* =====================================================================
   FAQs
   ===================================================================== */
Pages.faqs = async function (params, el) {
  const rows = await A.list('faqs');
  el.innerHTML = `
    <div class="page-head">
      <div><h1>FAQs</h1><p>${rows.length} question${rows.length === 1 ? '' : 's'}.</p></div>
      <div class="head-actions"><button class="btn btn-p" data-act="fq:new">＋ New FAQ</button></div>
    </div>
    <div class="card pad0"><div class="t-wrap"><table>
      <thead><tr><th>Question</th><th>Answer</th><th></th></tr></thead>
      <tbody>${rows.length ? rows.map(f => `<tr>
        <td class="t-title">${esc(f.question)}</td>
        <td class="t-sub">${esc((f.answer || '').slice(0, 140))}${(f.answer || '').length > 140 ? '…' : ''}</td>
        <td><div class="t-actions">
          <button class="btn btn-o btn-s" data-act="fq:edit" data-id="${f.id}">Edit</button>
          ${f.system_locked ? '' : `<button class="btn btn-d btn-s" data-act="fq:del" data-id="${f.id}">Del</button>`}
        </div></td></tr>`).join('') : emptyRow(3, 'No FAQs yet.')}</tbody>
    </table></div></div>`;
};
A.on('fq:new', () => faqDialog(null));
A.on('fq:edit', async (d) => faqDialog(await A.get('faq', d.id)));
A.on('fq:del', async (d) => {
  if (!await confirmDialog({ title: 'Delete this FAQ?', danger: true, okLabel: 'Delete' })) return;
  await A.act('api_delete_entry', { p_entity: 'faq', p_id: d.id });
  A.go('faqs');
});
function faqDialog(f) {
  f = f || {};
  openModal(`<h2>${f.id ? 'Edit' : 'New'} FAQ</h2>
    <div class="fg" style="margin-top:14px"><label>Question <span class="req">*</span></label>
      <input class="fc" id="fq-q" autofocus value="${attr(f.question || '')}"></div>
    <div class="fg"><label>Answer <span class="req">*</span></label>
      <textarea class="fc" id="fq-a" style="min-height:140px">${esc(f.answer || '')}</textarea></div>
    <div class="m-act"><button class="btn btn-o" data-act="modal:close">Cancel</button>
      <button class="btn btn-p" data-act="fq:save" data-id="${f.id || ''}">Save</button></div>`, { small: true });
}
A.on('fq:save', async (d) => {
  const r = await A.act('api_save_entry', {
    p_entity: 'faq', p_data: { id: d.id || null, question: val('fq-q'), answer: val('fq-a') }
  });
  if (r) { closeModal(); A.go('faqs'); }
});

/* =====================================================================
   ABOUT PAGE
   ===================================================================== */
let aboutQuill = null;
Pages.about = async function (params, el) {
  const a = await A.get('about') || {};
  el.innerHTML = `
    <div class="page-head">
      <div><h1>About page</h1><p>The story visitors read on /about.</p></div>
      <div class="head-actions"><button class="btn btn-p" data-act="about:save">Save page</button></div>
    </div>
    <div class="card">
      <div class="row">
        <div class="fg"><label>Title</label><input class="fc" id="ab-title" value="${attr(a.title || '')}"></div>
        <div class="fg"><label>Subtitle</label><input class="fc" id="ab-sub" value="${attr(a.subtitle || '')}"></div>
      </div>
      <div class="fg"><label>Content</label><div id="ab-editor"></div></div>
    </div>`;
  aboutQuill = new Quill('#ab-editor', {
    theme: 'snow',
    modules: { toolbar: [[{ header: [2, 3, false] }], ['bold', 'italic', 'underline'],
      [{ list: 'ordered' }, { list: 'bullet' }], ['link', 'image'], ['clean']] }
  });
  if (a.body) aboutQuill.root.innerHTML = a.body;
};
A.on('about:save', async () => {
  await A.act('api_save_entry', {
    p_entity: 'about',
    p_data: { title: val('ab-title'), subtitle: val('ab-sub'), body: aboutQuill?.root.innerHTML || '' }
  }, 'About page saved');
});

/* =====================================================================
   MESSAGES
   ===================================================================== */
Pages.messages = async function (params, el) {
  const rows = await A.list('messages');
  const unread = rows.filter(m => !m.is_read).length;
  el.innerHTML = `
    <div class="page-head">
      <div><h1>Messages</h1><p>${rows.length} total · ${unread} unread.</p></div>
      ${unread ? `<div class="head-actions"><button class="btn btn-o" data-act="msg:read-all">Mark all as read</button></div>` : ''}
    </div>
    <div class="card pad0"><div class="t-wrap"><table>
      <thead><tr><th>From</th><th>Message</th><th>Received</th><th></th></tr></thead>
      <tbody>${rows.length ? rows.map(m => `<tr>
        <td><div class="t-title">${esc(m.name)} ${m.is_read ? '' : '<span class="pill p-warn">new</span>'}</div>
          <div class="t-sub">${esc(m.email)}</div></td>
        <td class="t-sub">${esc((m.message || '').slice(0, 120))}${(m.message || '').length > 120 ? '…' : ''}</td>
        <td class="t-sub nowrap">${fmtAgo(m.created_at)}</td>
        <td><div class="t-actions">
          <button class="btn btn-o btn-s" data-act="msg:open" data-id="${m.id}">Read</button>
          <button class="btn btn-d btn-s" data-act="msg:del" data-id="${m.id}">Del</button>
        </div></td></tr>`).join('') : emptyRow(4, 'No messages yet.')}</tbody>
    </table></div></div>`;
  A.cache.messages = rows;
};
A.on('msg:open', async (d) => {
  const m = (A.cache.messages || []).find(x => String(x.id) === String(d.id));
  if (!m) return;
  openModal(`<h2>${esc(m.name)}</h2>
    <p class="muted" style="font-size:.8rem">${esc(m.email)} · ${fmtDate(m.created_at, true)}</p>
    <div class="modal-body" style="white-space:pre-wrap;color:var(--tx)">${esc(m.message)}</div>
    <div class="m-act">
      <a class="btn btn-o" href="mailto:${attr(m.email)}?subject=Re: your message">Reply by email</a>
      <button class="btn btn-p" data-act="modal:close">Close</button>
    </div>`, { small: true });
  if (!m.is_read) {
    await A.call('api_entry_action', { p_entity: 'message', p_id: String(m.id), p_action: 'read', p_value: { value: true } }).catch(() => {});
    m.is_read = true;
  }
});
A.on('msg:read-all', async () => {
  await A.act('api_entry_action', { p_entity: 'message', p_id: '0', p_action: 'read_all' });
  A.go('messages');
});
A.on('msg:del', async (d) => {
  if (!await confirmDialog({ title: 'Delete this message?', danger: true, okLabel: 'Delete' })) return;
  await A.act('api_delete_entry', { p_entity: 'message', p_id: d.id });
  A.go('messages');
});

/* =====================================================================
   SUBSCRIBERS
   ===================================================================== */
Pages.subscribers = async function (params, el) {
  const rows = await A.list('subscribers');
  el.innerHTML = `
    <div class="page-head">
      <div><h1>Subscribers</h1><p>${rows.filter(s => s.is_active).length} active of ${rows.length}.</p></div>
      <div class="head-actions"><button class="btn btn-o" data-act="sub:export">⬇ Export CSV</button></div>
    </div>
    <div class="card pad0"><div class="t-wrap"><table>
      <thead><tr><th>Name</th><th>Email</th><th>Joined</th><th>Status</th><th></th></tr></thead>
      <tbody>${rows.length ? rows.map(s => `<tr>
        <td class="t-title">${esc(s.name)}</td>
        <td class="t-sub">${esc(s.email)}</td>
        <td class="t-sub nowrap">${fmtDate(s.created_at)}</td>
        <td>${s.is_active ? '<span class="pill p-ok">active</span>' : '<span class="pill p-mute">unsubscribed</span>'}</td>
        <td><div class="t-actions">
          <button class="btn btn-o btn-s" data-act="sub:toggle" data-id="${s.id}" data-v="${s.is_active ? '' : '1'}">
            ${s.is_active ? 'Deactivate' : 'Reactivate'}</button>
          <button class="btn btn-d btn-s" data-act="sub:del" data-id="${s.id}">Del</button>
        </div></td></tr>`).join('') : emptyRow(5, 'No subscribers yet.')}</tbody>
    </table></div></div>`;
  A.cache.subscribers = rows;
};
A.on('sub:toggle', async (d) => {
  await A.act('api_entry_action', { p_entity: 'subscriber', p_id: d.id, p_action: 'active', p_value: { value: !!d.v } }, false);
  A.go('subscribers');
});
A.on('sub:del', async (d) => {
  if (!await confirmDialog({ title: 'Remove this subscriber?', danger: true, okLabel: 'Remove' })) return;
  await A.act('api_delete_entry', { p_entity: 'subscriber', p_id: d.id });
  A.go('subscribers');
});
A.on('sub:export', () => {
  const rows = A.cache.subscribers || [];
  const csv = ['name,email,active,joined'].concat(rows.map(s =>
    [s.name, s.email, s.is_active, s.created_at].map(v => `"${String(v ?? '').replace(/"/g, '""')}"`).join(','))).join('\n');
  const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
  const a = document.createElement('a');
  a.href = url; a.download = 'subscribers.csv'; a.click();
  URL.revokeObjectURL(url);
});
