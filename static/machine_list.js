document.addEventListener("DOMContentLoaded", function () {

document.getElementById("csv-export-btn").addEventListener("click", function () {
    const rows = document.querySelectorAll("table tbody tr");
    let csvContent = "data:text/csv;charset=utf-8,\uFEFF";

    const headers = Array.from(document.querySelectorAll("table thead th"))
                        .map(th => `"${th.textContent.trim()}"`)
                        .join(",");
    csvContent += headers + "\n";

    rows.forEach(row => {
        if (row.style.display !== "none") {
            const cols = Array.from(row.querySelectorAll("td")).map(td => {
                return `"${td.innerText.trim()}"`;
            });
            csvContent += cols.join(",") + "\n";
        }
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "machine_list.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});

});

function showLocationForm(machineId) {
    const form = document.getElementById('location-form-' + machineId);
    form.style.display = (form.style.display === 'none' || form.style.display === '') ? 'inline' : 'none';
}

function showShipmentDetails(machineId) {
    const popup = document.getElementById('shipment-details-popup-' + machineId);
    popup.style.display = 'flex';
}

function closePopup(machineId) {
    const popup = document.getElementById('shipment-details-popup-' + machineId);
    popup.style.display = 'none';
}

function clearShipmentFields(machineId) {
    document.getElementById('company-name-' + machineId).value = '';
    document.getElementById('shipment-site-' + machineId).value = '';
    document.getElementById('start-date-' + machineId).value = '';
    document.getElementById('end-date-' + machineId).value = '';
}

function toggleDeleteColumn() {
  const deleteCols = document.querySelectorAll('.delete-column');
  deleteCols.forEach(col => {
    if (col.style.display === 'none' || col.style.display === '') {
      col.style.display = 'table-cell'; // 表示
    } else {
      col.style.display = 'none'; // 非表示
    }
  });
}

function toggleEditMode(button) {
  const row = button.closest('tr');
  const machineId = row.dataset.machineId;

  const displayTexts = row.querySelectorAll('.display-text');
  const editInputs = row.querySelectorAll('.edit-input');

  // 編集モード判定
  const isEditing = editInputs[0].style.display === 'inline-block';

  if (isEditing) {
    // 「保存」状態 → サーバに送信して保存

    // 入力値取得
    const data = {
      name: editInputs[0].value.trim(),
      manufacturer: editInputs[1].value.trim(),
      serial_number: editInputs[2].value.trim()
    };

    fetch(`/update_machine/${machineId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()  // CSRFトークンを取得する関数を別途用意する必要あり
      },
      body: JSON.stringify(data)
    })
    .then(response => {
      if (!response.ok) throw new Error('更新失敗');
      return response.json();
    })
    .then(json => {
      // 保存成功したら編集モード解除＆表示更新
      editInputs.forEach(input => input.style.display = 'none');
      displayTexts.forEach((span, i) => {
        span.textContent = data[['name', 'manufacturer', 'serial_number'][i]];
        span.style.display = 'inline-block';
      });
      button.textContent = '編集';
    })
    .catch(err => {
      alert('保存に失敗しました: ' + err.message);
    });

  } else {
    // 編集開始 → input表示、テキスト非表示、ボタン名変更
    editInputs.forEach(input => input.style.display = 'inline-block');
    displayTexts.forEach(span => span.style.display = 'none');
    button.textContent = '保存';
  }
}

// CSRFトークンを<meta>タグから取得する例
function getCsrfToken() {
  const meta = document.querySelector('meta[name=csrf-token]');
  return meta ? meta.content : '';
}

function toggleStatusSelect(machineId) {
  const form = document.getElementById(`status-form-${machineId}`);
  form.style.display = (form.style.display === 'none' || form.style.display === '') ? 'inline-block' : 'none';
}

function cancelStatusChange(machineId) {
  const form = document.getElementById(`status-form-${machineId}`);
  form.style.display = 'none';
}


document.getElementById("search-button").addEventListener("click", filterTable);

document.getElementById("shippedOnlyCheckbox").addEventListener("change", filterTable);

function filterTable() {
    const filter = document.getElementById("search-input").value.toLowerCase();
    const shippedOnly = document.getElementById("shippedOnlyCheckbox").checked;
    const rows = document.querySelectorAll("#printable-table tbody tr");

    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const isShipped = row.classList.contains("shipped");

        const matchesText = text.includes(filter);
        const matchesShipped = shippedOnly ? isShipped : true;

        if (matchesText && matchesShipped) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    });
}






