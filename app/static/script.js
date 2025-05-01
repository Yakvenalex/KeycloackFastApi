const noteTitleInput = document.getElementById('note-title-input')
const noteDescInput = document.getElementById('note-desc-input')
const addNoteBtn = document.getElementById('add-note-btn')
const notesList = document.getElementById('notes-list')

// Modal Elements
const viewNoteModalElement = document.getElementById('viewNoteModal')
const editNoteModalElement = document.getElementById('editNoteModal')
const deleteConfirmModalElement = document.getElementById('deleteConfirmModal')

// Modal BS Instances (initialize later)
let viewNoteModal, editNoteModal, deleteConfirmModal

// Modal Content Elements
const viewNoteTitle = document.getElementById('viewNoteTitle')
const viewNoteDescription = document.getElementById('viewNoteDescription')
const viewNoteDate = document.getElementById('viewNoteDate')
const editNoteIdInput = document.getElementById('edit-note-id')
const editNoteTitleInput = document.getElementById('edit-note-title')
const editNoteDescriptionInput = document.getElementById(
  'edit-note-description'
)
const saveEditBtn = document.getElementById('save-edit-btn')
const deleteNoteIdInput = document.getElementById('delete-note-id')
const confirmDeleteBtn = document.getElementById('confirm-delete-btn')

const NOTES_STORAGE_KEY = 'mimoNotes_v2'
const loader = document.getElementById('loader')

function formatNoteDate(timestamp) {
  if (!timestamp) return ''
  try {
    const date = new Date(timestamp)
    return date.toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch (e) {
    console.error('Error formatting date:', e)
    return 'Неверная дата'
  }
}

function showLoader() {
  loader.classList.remove('d-none')
}

function hideLoader() {
  loader.classList.add('d-none')
}

async function getNotes() {
  try {
    showLoader()
    const response = await fetch('/api/notes')
    if (!response.ok) throw new Error('Ошибка получения заметок')
    const data = await response.json()
    return data.notes
  } catch (error) {
    console.error('Error fetching notes:', error)
    return []
  } finally {
    hideLoader()
  }
}

async function saveNotes(notes) {
  // Эта функция больше не нужна, так как мы сохраняем через API
}

function createNoteElement(note) {
  const colDiv = document.createElement('div')
  colDiv.classList.add('col')

  const noteCard = document.createElement('div')
  noteCard.classList.add('card', 'h-100', 'note')
  noteCard.dataset.id = note.id

  const cardBody = document.createElement('div')
  cardBody.classList.add('card-body')
  cardBody.style.cursor = 'pointer'
  cardBody.addEventListener('click', () => showViewModal(note))

  const title = document.createElement('h5')
  title.classList.add('card-title', 'note-title')
  title.textContent = note.title
  title.title = note.title

  const description = document.createElement('p')
  description.classList.add('card-text', 'note-description')
  description.textContent = note.content

  const dateSpan = document.createElement('small')
  dateSpan.classList.add('text-muted', 'd-block', 'mt-2', 'note-date')
  dateSpan.textContent = `Создано: ${formatNoteDate(note.created_at)}`

  cardBody.appendChild(title)
  cardBody.appendChild(description)
  cardBody.appendChild(dateSpan)

  const cardFooter = document.createElement('div')
  cardFooter.classList.add('card-footer', 'note-actions')

  const viewButton = document.createElement('button')
  viewButton.classList.add('btn', 'btn-sm', 'btn-info', 'view-btn')
  viewButton.innerHTML = '<i class="bi bi-eye"></i>'
  viewButton.title = 'Просмотр'
  viewButton.addEventListener('click', () => showViewModal(note))

  const editButton = document.createElement('button')
  editButton.classList.add('btn', 'btn-sm', 'btn-warning', 'edit-btn')
  editButton.innerHTML = '<i class="bi bi-pencil"></i>'
  editButton.title = 'Редактировать'
  editButton.addEventListener('click', () => showEditModal(note))

  const deleteButton = document.createElement('button')
  deleteButton.classList.add('btn', 'btn-sm', 'btn-danger', 'delete-btn')
  deleteButton.innerHTML = '<i class="bi bi-trash"></i>'
  deleteButton.title = 'Удалить'
  deleteButton.addEventListener('click', () => showDeleteModal(note.id))

  cardFooter.appendChild(viewButton)
  cardFooter.appendChild(editButton)
  cardFooter.appendChild(deleteButton)

  noteCard.appendChild(cardBody)
  noteCard.appendChild(cardFooter)

  colDiv.appendChild(noteCard)

  return colDiv
}

async function renderNotes() {
  const notes = await getNotes()
  notesList.innerHTML = ''
  if (notes.length === 0) {
    const emptyMsg = document.createElement('p')
    emptyMsg.classList.add('empty-notes-message')
    emptyMsg.textContent = 'Заметок пока нет. Добавьте первую!'
    notesList.appendChild(emptyMsg)
  } else {
    notes.forEach((note) => {
      const noteElement = createNoteElement(note)
      notesList.appendChild(noteElement)
    })
  }
}

function showViewModal(note) {
  viewNoteTitle.textContent = note.title
  viewNoteDescription.textContent = note.content
  viewNoteDate.textContent = `Создано: ${formatNoteDate(note.created_at)}`
  viewNoteModal.show()
}

function showEditModal(note) {
  editNoteIdInput.value = note.id
  editNoteTitleInput.value = note.title
  editNoteDescriptionInput.value = note.content
  editNoteModal.show()
}

function showDeleteModal(noteId) {
  deleteNoteIdInput.value = noteId
  deleteConfirmModal.show()
}

async function handleSaveNoteChanges() {
  const id = editNoteIdInput.value
  const newTitle = editNoteTitleInput.value.trim()
  const newDescription = editNoteDescriptionInput.value.trim()

  if (!newTitle) {
    alert('Заголовок не может быть пустым.')
    editNoteTitleInput.focus()
    return
  }

  try {
    showLoader()
    const response = await fetch(`/api/notes/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        title: newTitle,
        content: newDescription,
      }),
    })

    if (!response.ok) throw new Error('Ошибка обновления заметки')

    await renderNotes()
    editNoteModal.hide()
  } catch (error) {
    console.error('Error updating note:', error)
    alert('Ошибка при обновлении заметки')
    editNoteModal.hide()
  } finally {
    hideLoader()
  }
}

async function handleConfirmDelete() {
  const id = deleteNoteIdInput.value
  try {
    showLoader()
    const response = await fetch(`/api/notes/${id}`, {
      method: 'DELETE',
    })

    if (!response.ok) throw new Error('Ошибка удаления заметки')

    await renderNotes()
    deleteConfirmModal.hide()
  } catch (error) {
    console.error('Error deleting note:', error)
    alert('Ошибка при удалении заметки')
    deleteConfirmModal.hide()
  } finally {
    hideLoader()
  }
}

async function addNote() {
  const title = noteTitleInput.value.trim()
  const description = noteDescInput.value.trim()

  if (title) {
    try {
      showLoader()
      const response = await fetch('/api/notes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: title,
          content: description,
        }),
      })

      if (!response.ok) throw new Error('Ошибка добавления заметки')

      noteTitleInput.value = ''
      noteDescInput.value = ''
      await renderNotes()
    } catch (error) {
      console.error('Error adding note:', error)
      alert('Ошибка при добавлении заметки')
    } finally {
      hideLoader()
    }
  } else {
    alert('Пожалуйста, введите заголовок заметки.')
    noteTitleInput.focus()
  }
}

document.addEventListener('DOMContentLoaded', () => {
  if (typeof bootstrap === 'undefined') {
    console.error('Bootstrap Bundle not loaded!')
    return
  }
  viewNoteModal = new bootstrap.Modal(viewNoteModalElement)
  editNoteModal = new bootstrap.Modal(editNoteModalElement)
  deleteConfirmModal = new bootstrap.Modal(deleteConfirmModalElement)

  renderNotes()
})

addNoteBtn.addEventListener('click', addNote)
saveEditBtn.addEventListener('click', handleSaveNoteChanges)
confirmDeleteBtn.addEventListener('click', handleConfirmDelete)

// Добавляем обработчик для кнопки выхода
document
  .querySelector('a[href="/api/logout"]')
  .addEventListener('click', (e) => {
    e.preventDefault()
    showLoader()
    window.location.href = '/api/logout'
  })
