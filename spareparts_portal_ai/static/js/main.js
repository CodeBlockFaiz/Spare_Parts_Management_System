document.addEventListener('DOMContentLoaded',()=>{
  const add = document.getElementById('add-line');
  const lines = document.getElementById('lines');
  if(!add || !lines) return;
  let i=0;
  add.addEventListener('click',()=>{
    const el = document.createElement('div');
    el.className='line';
    el.innerHTML = `
      <select name="part_${i}" required>
        <option value="">-- select part --</option>
        ${ (window.parts||[]).map(p=>`<option value="${p.id}">${p.label}</option>`).join('') }
      </select>
      <input type="number" name="qty_${i}" min="1" value="1" style="width:80px" />
      <button type="button" class="btn remove">Remove</button>
    `;
    lines.appendChild(el);
    i++;
    el.querySelector('.remove').addEventListener('click',()=> el.remove());
  });
});
