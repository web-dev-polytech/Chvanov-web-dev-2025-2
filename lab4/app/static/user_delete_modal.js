'use strict';

function modalShown(event) {
    let button = event.relatedTarget;
    let fullname = button.dataset.userFullname;
    let deleteUrl = button.dataset.deleteUrl;
    let form = document.getElementById('deleteModalForm');
    document.getElementById('deleteUserFullname').textContent = fullname;
    form.action = deleteUrl;
}

let modal = document.getElementById('deleteModal');
modal.addEventListener('show.bs.modal', modalShown);
