let currentLang = localStorage.getItem('appLang') || 'en';
let editingUserId = null;

function setLang(lang) {
    currentLang = lang;
    localStorage.setItem('appLang', lang);
    
    document.getElementById('btn-en').classList.toggle('active', lang === 'en');
    document.getElementById('btn-uk').classList.toggle('active', lang === 'uk');

    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[lang] && translations[lang][key]) {
            el.innerText = translations[lang][key];
        }
    });

    document.getElementById('username').placeholder = translations[lang].placeholder_username;
    document.getElementById('name').placeholder = translations[lang].placeholder_name;
    document.getElementById('email').placeholder = translations[lang].placeholder_email;

    // Update dynamic texts
    if (editingUserId) {
        document.getElementById('formTitle').innerText = t('edit_user_title');
        document.getElementById('submitBtnText').innerText = t('btn_save');
    }

    const tbody = document.getElementById('usersBody');
    if (tbody && (tbody.querySelector('.loading-state') || tbody.querySelector('.error-state'))) {
        loadUsers(); 
    }
}

function t(key) { 
    return translations[currentLang][key] || key; 
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    const toastIcon = document.getElementById('toastIcon');
    
    toast.className = `toast show ${type}`;
    toastMessage.textContent = message;
    
    if (type === 'success') {
        toastIcon.innerHTML = '<svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>';
    } else {
        toastIcon.innerHTML = '<svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>';
    }
    
    setTimeout(() => toast.classList.remove('show'), 4000);
}

function setButtonLoading(btn, isLoading, originalText, loadingKey) {
    if (isLoading) {
        btn.disabled = true;
        btn.innerHTML = `<span class="spinner"></span> ${t(loadingKey)}`;
    } else {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

async function loadUsers() {
    const tbody = document.getElementById('usersBody');
    const refreshBtn = document.getElementById('refreshBtn');
    if (!tbody || !refreshBtn) return;

    const originalBtnHTML = refreshBtn.innerHTML; 
    
    setButtonLoading(refreshBtn, true, originalBtnHTML, 'msg_processing');
    
    try {
        tbody.innerHTML = `<tr><td colspan="6" class="loading-state"><span class="spinner"></span> ${t('msg_fetch')}</td></tr>`;
        
        // Додаємо ?t=timestamp, щоб браузер не кешував результати GET запиту
        const response = await fetch('/api/users?t=' + new Date().getTime());
        const users = await response.json();
        
        if (users.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="loading-state">${t('msg_empty')}</td></tr>`;
            setButtonLoading(refreshBtn, false, originalBtnHTML, 'msg_processing');
            return;
        }

        tbody.innerHTML = users.map(u => {
            const encodedUser = encodeURIComponent(JSON.stringify(u));
            return `
            <tr style="animation: slideUp 0.3s ease forwards; opacity: 0;">
                <td class="tech-font highlight-id">#${u.id}</td>
                <td class="tech-font highlight-user">@${u.username}</td>
                <td>${u.name || '-'}</td>
                <td class="tech-font text-muted">${u.email || '-'}</td>
                <td class="tech-font">${u.age || '-'}</td>
                <td style="text-align: right; display: flex; gap: 0.25rem; justify-content: flex-end;">
                    <button class="btn-icon btn-icon-edit" onclick="startEdit('${encodedUser}')" title="Edit">
                        <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg>
                    </button>
                    <button class="btn-icon" onclick="deleteUser(${u.id})" title="Delete">
                        <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                    </button>
                </td>
            </tr>
        `}).join('');
        
        const rows = tbody.querySelectorAll('tr');
        rows.forEach((row, index) => {
            row.style.animationDelay = `${index * 0.05}s`;
        });
    } catch (error) {
        console.error("Fetch Error:", error);
        tbody.innerHTML = `<tr><td colspan="6" class="error-state">Error: ${error.message}</td></tr>`;
        showToast("Error: " + error.message, "error");
    } finally {
        setButtonLoading(refreshBtn, false, originalBtnHTML, 'msg_processing');
    }
}

function startEdit(encodedUser) {
    const u = JSON.parse(decodeURIComponent(encodedUser));
    editingUserId = u.id;
    
    const form = document.getElementById('addUserForm');
    form.username.value = u.username;
    form.username.disabled = false; // Тепер username можна змінювати!
    form.name.value = u.name || '';
    form.email.value = u.email || '';
    form.age.value = u.age || '';

    document.getElementById('formTitle').innerText = t('edit_user_title');
    document.getElementById('submitBtnText').innerText = t('btn_save');
    document.getElementById('cancelBtn').style.display = 'block';

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function cancelEdit() {
    editingUserId = null;
    const form = document.getElementById('addUserForm');
    if (form) {
        form.reset();
        form.username.disabled = false;
    }
    
    const formTitle = document.getElementById('formTitle');
    if (formTitle) formTitle.innerText = t('add_user_title');
    
    const submitBtnText = document.getElementById('submitBtnText');
    if (submitBtnText) submitBtnText.innerText = t('btn_create');
    
    const cancelBtn = document.getElementById('cancelBtn');
    if (cancelBtn) cancelBtn.style.display = 'none';
}

async function submitUser(event) {
    event.preventDefault();
    const form = event.target;
    const btn = document.getElementById('submitBtn');
    const originalBtnHTML = btn.innerHTML;
    
    const userData = {
        username: form.username.value,
        name: form.name.value,
        email: form.email.value,
        age: form.age.value ? parseInt(form.age.value) : null
    };

    setButtonLoading(btn, true, originalBtnHTML, 'msg_processing');

    try {
        const method = editingUserId ? 'PUT' : 'POST';
        const url = editingUserId ? `/api/users/${editingUserId}` : '/api/users';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });

        const result = await response.json();

        if (response.ok) {
            showToast(editingUserId ? t('toast_put_success') : t('toast_success'), "success");
            editingUserId = null; // Очищаємо статус редагування перед finally
            loadUsers(); 
        } else {
            showToast(result.error || "Error", "error");
        }
    } catch (error) {
        console.error("Submit Error:", error);
        showToast("Error: " + error.message, "error");
    } finally {
        setButtonLoading(btn, false, originalBtnHTML, 'msg_processing');
        if (!editingUserId) {
            cancelEdit(); // Відновлюємо форму тільки після того, як кнопка повернула свій HTML
        }
    }
}

async function deleteUser(id) {
    if (!confirm(currentLang === 'uk' ? 'Ви впевнені, що хочете видалити цього користувача?' : 'Are you sure you want to delete this user?')) return;
    try {
        const response = await fetch(`/api/users/${id}`, { method: 'DELETE' });
        if (response.ok) {
            showToast(t('toast_del_success'), "success");
            loadUsers();
        } else {
            const result = await response.json();
            showToast(result.error || t('toast_del_err'), "error");
        }
    } catch (error) { 
        console.error("Delete Error:", error);
        showToast("Error: " + error.message, "error"); 
    }
}

document.addEventListener('DOMContentLoaded', () => { 
    setLang(currentLang); 
});
