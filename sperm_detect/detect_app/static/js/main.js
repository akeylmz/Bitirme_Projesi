document.addEventListener('DOMContentLoaded', function() {
    const videoInput = document.getElementById('videoInput');
    const uploadContainer = document.querySelector('.upload-container');

    videoInput.addEventListener('change', function() {
        const file = this.files[0];

        if (file) {
            const reader = new FileReader();

            reader.addEventListener('load', function() {
                uploadContainer.style.backgroundImage = `url(${this.result})`;
                uploadContainer.style.backgroundSize = 'cover';
                uploadContainer.style.backgroundPosition = 'center';

                const fileName = file.name;
                uploadContainer.innerHTML = fileName;  // Dosya adını göster
            });

            reader.readAsDataURL(file);
        }
    });
});
