function enableDragAndDrop() {
  const lists = document.querySelectorAll('.kanban-list');
  const items = document.querySelectorAll('.kanban-item');

  items.forEach(item => {
    item.addEventListener('dragstart', (e) => {
      e.dataTransfer.setData('text/plain', item.dataset.id);
      item.classList.add('dragging');
    });
    item.addEventListener('dragend', () => {
      item.classList.remove('dragging');
    });
  });

  lists.forEach(list => {
    list.addEventListener('dragover', (e) => {
      e.preventDefault();
      const dragging = document.querySelector('.dragging');
      const afterElement = getDragAfterElement(list, e.clientY);
      if (afterElement == null) {
        list.appendChild(dragging);
      } else {
        list.insertBefore(dragging, afterElement);
      }
    });

    list.addEventListener('drop', async (e) => {
      e.preventDefault();
      const status = list.parentElement.getAttribute('data-status');
      const items = Array.from(list.querySelectorAll('.kanban-item'));
      const draggingId = e.dataTransfer.getData('text/plain');
      const newPosition = items.findIndex(i => i.dataset.id === draggingId) + 1;
      if (!window.jwtToken) {
        await fetchToken();
      }
      await fetch('/api/tasks/reorder', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + window.jwtToken
        },
        body: JSON.stringify({ task_id: parseInt(draggingId), new_status: status, new_position: newPosition })
      });
    });
  });
}

function getDragAfterElement(container, y) {
  const draggableElements = [...container.querySelectorAll('.kanban-item:not(.dragging)')];
  return draggableElements.reduce((closest, child) => {
    const box = child.getBoundingClientRect();
    const offset = y - box.top - box.height / 2;
    if (offset < 0 && offset > closest.offset) {
      return { offset: offset, element: child };
    } else {
      return closest;
    }
  }, { offset: Number.NEGATIVE_INFINITY }).element;
}

document.addEventListener('DOMContentLoaded', enableDragAndDrop);