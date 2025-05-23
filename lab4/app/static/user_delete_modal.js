'use strict';

function modalShown(event) {
    let button = event.relatedTarget;
    let userId = button.dataset.userId;
    let fullname = button.dataset.userFullname;
    let newUrl = `/users/${userId}/delete`;
    let form = document.getElementById('deleteModalForm');
    document.getElementById('deleteUserFullname').textContent = fullname;
    form.action = newUrl;
}

let modal = document.getElementById('deleteModal');
modal.addEventListener('show.bs.modal', modalShown);
