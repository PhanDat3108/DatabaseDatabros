function toggleDisplayFlex(id) {
  const el = document.getElementById(id);
  const allBoxes = document.querySelectorAll('.form-box');

  allBoxes.forEach(box => {
    if (box.id === id) {
      // Hiện nếu đang ẩn, ẩn nếu đang hiện
      if (el.style.display === "none" || el.style.display === "") {
        el.style.display = "flex";
        el.style.flexDirection = "column";
      } else {
        el.style.display = "none";
      }
    } else {
      box.style.display = "none"; // Ẩn các box khác
    }
  });
}
function toggleDisplayFlexx(id) {
  const allBoxes = document.querySelectorAll('.form-box');
  allBoxes.forEach(box => {
    if (box.id === id) {
      // Toggle: hiện nếu đang ẩn, ẩn nếu đang hiện
      const isHidden = box.style.display === "none" || box.style.display === "";
      box.style.display = isHidden ? "flex" : "none";
      if (isHidden) box.style.flexDirection = "column";
    } else {
      box.style.display = "none"; // Ẩn các box còn lại
    }
  });
}

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("luggageForm");

  form.addEventListener("submit", function (e) {
    e.preventDefault(); // ✅ Ngăn form load lại trang

    const formData = new FormData(form);

    fetch("/add_luggage", {
      method: "POST",
      body: formData
    })
    .then(response => response.text())
    .then(data => {
      alert(data); // ✅ Hiện kết quả (Thành công hoặc lỗi)
      form.reset(); // ✅ Reset form nếu muốn
    })
    .catch(error => {
      alert("Lỗi gửi dữ liệu: " + error);
    });
  });



  
  const ticketForm = document.getElementById("ticketForm");
  if (ticketForm) {
    ticketForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const formData = new FormData(ticketForm);

      fetch("/book_ticket", {
        method: "POST",
        body: formData
      })
      .then(response => response.text())
      .then(data => {
        alert(data);
        ticketForm.reset();
      })
      .catch(error => alert("Lỗi khi đặt vé: " + error));
    });
  }

});
function editTicket(ticket) {
  document.getElementById('edit_mave').value = ticket.MaVe;
  document.getElementById('edit_soghe').value = ticket.SoGhe;
  document.getElementById('edit_hangve').value = ticket.HangVe;
  document.getElementById('edit_giave').value = ticket.GiaVe;
  document.getElementById('edit_trangthai').value = ticket.TrangThaiThanhToan;
}
function editSelectedTicket() {
  // Tìm dòng đầu tiên trong bảng kết quả
  const table = document.getElementById("ticketTable");
  const firstRow = table ? table.rows[1] : null; // rows[0] là header

  if (!firstRow) {
    alert("Không có vé nào để sửa!");
    return;
  }

  // Lấy dữ liệu từ các ô (td) trong dòng đầu tiên
  const cells = firstRow.cells;

  // Gán vào form sửa (theo đúng thứ tự cột bảng)
  document.getElementById('edit_mave').value = cells[3].innerText;  // Mã vé
  document.getElementById('edit_soghe').value = cells[4].innerText;
  document.getElementById('edit_hangve').value = cells[5].innerText;
  document.getElementById('edit_giave').value = cells[6].innerText;
  document.getElementById('edit_trangthai').value = cells[7].innerText;
}
// Khi bấm nút "Sửa vé"
function openEditTicketForm(maVe) {
    localStorage.setItem("editVe", maVe);
    document.getElementById(`edit-ticket-${maVe}`).style.display = 'block';
}
function openEditLuggageForm(maHL) {
    localStorage.setItem("editHanhLy", maHL);
    document.getElementById(`edit-luggage-${maHL}`).style.display = 'block';
}
function editSelectedFlight() {
  const table = document.getElementById("flightTable");
  const rows = table.getElementsByTagName("tr");
  if (rows.length < 2) return alert("Không có chuyến bay để sửa.");

  const firstRow = rows[1]; // Lấy dòng đầu tiên (sau tiêu đề)
  const cells = firstRow.getElementsByTagName("td");

  document.getElementById("edit_machuyenbay").value = cells[0].innerText;
  document.getElementById("edit_mamaybay").value = cells[1].innerText;
  document.getElementById("edit_sohieu").value = cells[2].innerText;
  document.getElementById("edit_masanbaydoitac").value = cells[3].innerText;
  document.getElementById("edit_huongbay").value = cells[4].innerText;
  document.getElementById("edit_trangthai").value = cells[5].innerText;
}