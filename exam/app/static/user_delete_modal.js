'use strict';

function modalShown(event) {
    let button = event.relatedTarget;
    let event_name = button.dataset.eventName;
    let deleteUrl = button.dataset.deleteUrl;
    let form = document.getElementById('deleteModalForm');
    document.getElementById('deleteEventName').textContent = event_name;
    form.action = deleteUrl;
}

let modal = document.getElementById('deleteModal');
modal.addEventListener('show.bs.modal', modalShown);
