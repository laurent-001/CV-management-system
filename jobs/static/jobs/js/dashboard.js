document.addEventListener('DOMContentLoaded', function () {
    const scriptTag = document.querySelector('script[src*="dashboard.js"]');
    const profileImageUploadUrl = scriptTag.dataset.profileImageUploadUrl;
    const cvUploadUrl = scriptTag.dataset.cvUploadUrl;

    const uploadProfileImageBtn = document.getElementById('upload-profile-image-btn');
    const uploadCvBtn = document.getElementById('upload-cv-btn');
    const profileImageInput = document.getElementById('profile_picture');
    const cvInput = document.getElementById('cv');

    if (uploadProfileImageBtn) {
        uploadProfileImageBtn.addEventListener('click', function (e) {
            e.preventDefault();
            profileImageInput.click();
        });
    }

    if (uploadCvBtn) {
        uploadCvBtn.addEventListener('click', function (e) {
            e.preventDefault();
            cvInput.click();
        });
    }

    if (profileImageInput) {
        profileImageInput.addEventListener('change', function () {
            const formData = new FormData();
            formData.append('profile_picture', this.files[0]);

            fetch(profileImageUploadUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.querySelector('.profile-image img').src = data.profile_image_url;
                    showNotification('Profile image updated successfully.');
                }
            });
        });
    }

    if (cvInput) {
        cvInput.addEventListener('change', function () {
            const formData = new FormData();
            formData.append('cv', this.files[0]);

            fetch(cvUploadUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const downloadBtn = document.querySelector('.details-card a[download]');
                    if (downloadBtn) {
                        downloadBtn.href = data.cv_url;
                    } else {
                        const cvCard = document.querySelector('.details-card:last-child');
                        cvCard.innerHTML = `<h3>Curriculum Vitae (CV)</h3><a href="${data.cv_url}" class="btn btn-secondary" download>Download CV</a>`;
                    }
                    showNotification('CV uploaded successfully.');
                }
            });
        });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function showNotification(message) {
        const toast = document.getElementById('notification-toast');
        if (toast) {
            toast.textContent = message;
            toast.classList.add('show');

            // Hide the toast after 3 seconds
            setTimeout(() => {
                toast.classList.remove('show');
            }, 3000);
        }
    }
});
