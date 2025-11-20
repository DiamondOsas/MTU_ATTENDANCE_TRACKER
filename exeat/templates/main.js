const apiUrl = '/exeat';

document.addEventListener('DOMContentLoaded', () => {
  const newBtn = document.getElementById('newBtn');
  const formContainer = document.getElementById('formContainer');
  const listContainer = document.getElementById('listContainer');
  const cancelBtn = document.getElementById('cancelBtn');
  const exeatForm = document.getElementById('exeatForm');
  const exeatTableBody = document.querySelector('#exeatTable tbody');
  const formTitle = document.getElementById('formTitle');
  const exeatIdInput = document.getElementById('exeatId');

  newBtn.addEventListener('click', () => {
    formTitle.textContent = 'New Exeat';
    exeatIdInput.value = '';
    exeatForm.reset();
    formContainer.classList.remove('hidden');
    listContainer.classList.add('hidden');
  });

  cancelBtn.addEventListener('click', () => {
    formContainer.classList.add('hidden');
    listContainer.classList.remove('hidden');
  });

  exeatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = exeatIdInput.value;
    const payload = {
      first_name: document.getElementById('first_name').value,
      surname: document.getElementById('surname').value,
      level: parseInt(document.getElementById('level').value, 10),
      chapel_line: parseInt(document.getElementById('chapel_line').value, 10),
      chapel_seat: parseInt(document.getElementById('chapel_seat').value, 10),
      absent_start: document.getElementById('absent_start').value,
      absent_end: document.getElementById('absent_end').value || document.getElementById('absent_start').value
    };

    let method = 'POST';
    let url = apiUrl;
    if (id) {
      method = 'PUT';
      url = `${apiUrl}/${id}`;
    }

    const resp = await fetch(url, {
      method: method,
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    if (resp.ok) {
      formContainer.classList.add('hidden');
      listContainer.classList.remove('hidden');
      loadList();
    } else {
      const err = await resp.json();
      alert('Error: ' + (err.error || JSON.stringify(err)));
    }
  });

  async function loadList() {
    const resp = await fetch(apiUrl);
    const data = await resp.json();
    exeatTableBody.innerHTML = '';
    data.forEach(rec => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${rec.id}</td>
        <td>${rec.first_name} ${rec.surname}</td>
        <td>${rec.level}</td>
        <td>Line ${rec.chapel_line}, Seat ${rec.chapel_seat}</td>
        <td>${rec.absent_start}${rec.absent_end && rec.absent_end !== rec.absent_start ? ' → '+rec.absent_end : ''}</td>
        <td>
          <button data-id="${rec.id}" class="editBtn">Edit</button>
          <button data-id="${rec.id}" class="deleteBtn">Delete</button>
        </td>
      `;
      exeatTableBody.appendChild(tr);
    });
    // attach edit & delete handlers
    document.querySelectorAll('.editBtn').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = btn.getAttribute('data-id');
        const rec = (await fetch(apiUrl)).ok ? (await (await fetch(apiUrl)).json()).find(r => r.id == id) : null;
        if (!rec) {
          alert('Record not found');
          return;
        }
        formTitle.textContent = 'Edit Exeat';
        exeatIdInput.value = rec.id;
        document.getElementById('first_name').value = rec.first_name;
        document.getElementById('surname').value = rec.surname;
        document.getElementById('level').value = rec.level;
        document.getElementById('chapel_line').value = rec.chapel_line;
        document.getElementById('chapel_seat').value = rec.chapel_seat;
        document.getElementById('absent_start').value = rec.absent_start;
        document.getElementById('absent_end').value = rec.absent_end;
        formContainer.classList.remove('hidden');
        listContainer.classList.add('hidden');
      });
    });
    document.querySelectorAll('.deleteBtn').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = btn.getAttribute('data-id');
        if (!confirm('Delete record id '+id+' ?')) return;
        const resp = await fetch(`${apiUrl}/${id}`, { method: 'DELETE' });
        if (resp.ok) {
          loadList();
        } else {
          const err = await resp.json();
          alert('Error: ' + (err.error || JSON.stringify(err)));
        }
      });
    });
  }

  // initial load
  loadList();
});
