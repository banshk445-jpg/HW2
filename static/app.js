document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('file-input');
    const dropZone = document.getElementById('drop-zone');
    
    const uploadSection = document.getElementById('upload-section');
    const previewSection = document.getElementById('preview-section');
    const resultSection = document.getElementById('result-section');
    
    const previewImage = document.getElementById('preview-image');
    const analyzeBtn = document.getElementById('analyze-btn');
    const resetBtn = document.getElementById('reset-btn');
    const tryAgainBtn = document.getElementById('try-again-btn');
    
    const imageWrapper = document.querySelector('.image-wrapper');
    const loadingText = document.getElementById('loading-text');
    const matchName = document.getElementById('match-name');
    const similarityValue = document.getElementById('similarity-value');
    const similarityFill = document.getElementById('similarity-fill');
    
    let currentUploadedFile = null;

    // Drag & Drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    function handleFile(file) {
        if (!file.type.startsWith('image/')) {
            alert('이미지 파일만 업로드 가능합니다.');
            return;
        }
        currentUploadedFile = file;
        
        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.src = e.target.result;
            uploadSection.classList.add('hidden');
            previewSection.classList.remove('hidden');
            resetBtn.classList.remove('hidden');
        };
        reader.readAsDataURL(file);
    }

    analyzeBtn.addEventListener('click', async () => {
        if (!currentUploadedFile) return;
        
        // Setup loading state
        analyzeBtn.classList.add('hidden');
        resetBtn.classList.add('hidden');
        loadingText.classList.remove('hidden');
        imageWrapper.classList.add('scanning');
        
        // Call API
        const formData = new FormData();
        formData.append('file', currentUploadedFile);
        
        try {
            const response = await fetch('/api/v1/predict', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            if(data.success) {
                showResult(data.match_name, data.similarity);
            } else {
                alert('에러가 발생했습니다: ' + data.message);
                resetUI();
            }
        } catch (error) {
            console.error('Error:', error);
            alert('서버와 통신하는 중 문제가 발생했습니다.');
            resetUI();
        }
    });

    function showResult(name, similarity) {
        previewSection.classList.add('hidden');
        imageWrapper.classList.remove('scanning');
        loadingText.classList.add('hidden');
        
        resultSection.classList.remove('hidden');
        
        matchName.textContent = name;
        
        // 0부터 대상 수치까지 애니메이션 숫자 카운트업
        let currentSim = 0;
        const targetSim = similarity;
        const duration = 1500;
        const interval = 20;
        const step = targetSim / (duration / interval);
        
        const timer = setInterval(() => {
            currentSim += step;
            if (currentSim >= targetSim) {
                currentSim = targetSim;
                clearInterval(timer);
            }
            similarityValue.textContent = currentSim.toFixed(1);
        }, interval);
        
        // Fill bar animation
        setTimeout(() => {
            similarityFill.style.width = similarity + '%';
        }, 100);
    }

    function resetUI() {
        currentUploadedFile = null;
        fileInput.value = '';
        
        uploadSection.classList.remove('hidden');
        previewSection.classList.add('hidden');
        resultSection.classList.add('hidden');
        
        analyzeBtn.classList.remove('hidden');
        resetBtn.classList.add('hidden');
        imageWrapper.classList.remove('scanning');
        loadingText.classList.add('hidden');
        
        similarityFill.style.width = '0%';
    }

    resetBtn.addEventListener('click', resetUI);
    tryAgainBtn.addEventListener('click', resetUI);

    // Simple dot animation on text
    setInterval(() => {
        const dots = document.querySelector('.dots');
        if(dots) {
            if(dots.textContent.length >= 3) dots.textContent = '';
            else dots.textContent += '.';
        }
    }, 500);
});
