document.addEventListener('DOMContentLoaded', function() {
    const videoInput = document.getElementById('videoInput');
    const uploadContainer = document.querySelector('.upload-container');
    const videoElement = document.createElement('video');
    videoElement.setAttribute('controls', '');

    videoInput.addEventListener('change', function() {
        const file = this.files[0];

        if (file) {
            const reader = new FileReader();

            reader.addEventListener('load', function() {
                const videoUrl = URL.createObjectURL(file);
                videoElement.src = videoUrl;
                uploadContainer.innerHTML = '';  // Container'ı temizle
                uploadContainer.appendChild(videoElement);
            });

            reader.readAsDataURL(file);
        }
    });
});
