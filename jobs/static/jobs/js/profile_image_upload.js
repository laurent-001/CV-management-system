document.addEventListener("DOMContentLoaded", function () {
    const imageWrapper = document.getElementById("profileImageWrapper");
    const imagePreview = document.getElementById("imagePreview");
    const imageInput = document.getElementById("profileImageInput");
    const removeButton = document.getElementById("removeProfileImageBtn");
    const uploadStatus = document.getElementById("uploadStatus");
    const csrfToken = getCookie("csrftoken");

    // Function to get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === name + "=") {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Trigger file input when the image wrapper is clicked
    if (imageWrapper) {
        imageWrapper.addEventListener("click", () => imageInput.click());
    }

    // Handle file selection
    if (imageInput) {
        imageInput.addEventListener("change", (event) => {
            const file = event.target.files[0];
            if (file) {
                handleFile(file);
            }
        });
    }

    // --- Drag and Drop ---
    if (imageWrapper) {
        imageWrapper.addEventListener("dragenter", (e) => {
            e.preventDefault();
            e.stopPropagation();
            imageWrapper.classList.add("dragover");
        });

        imageWrapper.addEventListener("dragover", (e) => {
            e.preventDefault();
            e.stopPropagation();
            imageWrapper.classList.add("dragover");
        });

        imageWrapper.addEventListener("dragleave", (e) => {
            e.preventDefault();
            e.stopPropagation();
            imageWrapper.classList.remove("dragover");
        });

        imageWrapper.addEventListener("drop", (e) => {
            e.preventDefault();
            e.stopPropagation();
            imageWrapper.classList.remove("dragover");
            const file = e.dataTransfer.files[0];
            if (file) {
                handleFile(file);
            }
        });
    }

    // Handle the selected file
    function handleFile(file) {
        // Frontend validation
        const allowedTypes = ["image/jpeg", "image/png", "image/jpg"];
        if (!allowedTypes.includes(file.type)) {
            showStatusMessage("Only JPG, JPEG, and PNG formats are allowed.", "error");
            return;
        }

        if (file.size > 2 * 1024 * 1024) { // 2MB
            showStatusMessage("Image file too large ( > 2MB )", "error");
            return;
        }

        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
        };
        reader.readAsDataURL(file);

        // Upload the file
        uploadFile(file);
    }

    // Upload the file via Fetch API
    function uploadFile(file) {
        const formData = new FormData();
        formData.append("profile_picture", file);

        showStatusMessage("Uploading...", "info");

        fetch("/profile/upload-image/", {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,
            },
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                imagePreview.src = data.profile_image_url + `?t=${new Date().getTime()}`; // Add timestamp to break cache
                showStatusMessage("Profile image updated successfully.", "success");
            } else {
                const errorMessage = Object.values(data.errors).flat().join(" ");
                showStatusMessage(errorMessage || "Upload failed.", "error");
            }
        })
        .catch(error => {
            console.error("Error:", error);
            showStatusMessage("An unexpected error occurred.", "error");
        });
    }

    // Handle remove button click
    if (removeButton) {
        removeButton.addEventListener("click", () => {
            fetch("/profile/remove-image/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    imagePreview.src = data.profile_image_url;
                    showStatusMessage("Profile image removed.", "success");
                } else {
                    showStatusMessage("Failed to remove image.", "error");
                }
            })
            .catch(error => {
                console.error("Error:", error);
                showStatusMessage("An unexpected error occurred.", "error");
            });
        });
    }

    // Function to display status messages
    function showStatusMessage(message, type) {
        uploadStatus.innerHTML = `<span class="${type}-message">${message}</span>`;
    }
});
