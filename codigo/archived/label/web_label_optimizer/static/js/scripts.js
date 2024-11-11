document.addEventListener('DOMContentLoaded', function() {
    const uploadSection = document.getElementById('uploadSection');
    const configSection = document.getElementById('configSection');
    const cropSection = document.getElementById('cropSection');
    const segmentationSection = document.getElementById('segmentationSection');
    const dropArea = document.getElementById('dropArea');
    const videoInput = document.getElementById('videoInput');
    const uploadButton = document.getElementById('uploadButton');
    const fragmentButton = document.getElementById('fragmentButton');
    const previousButton = document.getElementById('previousButton');
    const nextButton = document.getElementById('nextButton');
    const cropButton = document.getElementById('cropButton');
    const image = document.getElementById('image');
    const imageSegmentation = document.getElementById('imageSegmentation');
    const cropArea = document.getElementById('cropArea');
    const statusMessage = document.getElementById('statusMessage');
    const cropCountElement = document.getElementById('cropCount');
    const segmentationCanvas = document.getElementById('segmentationCanvas');
    const applySegmentationButton = document.getElementById('applySegmentationButton');
    const previousButtonSegmentation = document.getElementById('previousButtonSegmentation');
    const nextButtonSegmentation = document.getElementById('nextButtonButtonSegmentation');
    const showSegmentationButton = document.getElementById('showSegmentationButton');


    const maskSection = document.getElementById('maskSection');
    const maskImage = document.getElementById('maskImage');
    const maskRectBlue = document.getElementById('maskRectBlue');
    const maskRect1 = document.getElementById('maskRect1');
    const maskRect2 = document.getElementById('maskRect2');
    const applyMaskButton = document.getElementById('applyMaskButton');
    const previousButtonMask = document.getElementById('previousButtonMask');
    const nextButtonMask = document.getElementById('nextButtonMask');
    

    const maskContainer = document.getElementById('maskContainer');

    maskRectBlue.style.position = 'absolute';
    maskRectBlue.style.border = '2px solid blue';
    maskRectBlue.style.backgroundColor = 'rgba(0, 0, 255, 0.2)';
    maskRectBlue.style.zIndex = '9999';

    maskRect1.style.position = 'absolute';
    maskRect1.style.border = '2px solid red';
    maskRect1.style.backgroundColor = 'rgba(255, 0, 0, 0.2)';
    maskRect1.style.zIndex = '9999';

    maskRect2.style.position = 'absolute';
    maskRect2.style.border = '2px solid red';
    maskRect2.style.backgroundColor = 'rgba(255, 0, 0, 0.2)';
    maskRect2.style.zIndex = '9999';

    maskContainer.style.position = 'relative';

    let uploadedImages = [];
    let currentImageIndex = 0;

    let maskImages = [];
    let currentMaskIndex = 0;

    showMaskButton.addEventListener('click', showMaskSection);

    function showMaskSection() {
        document.querySelectorAll('.section').forEach(section => {
            section.style.display = 'none';
        });
        maskSection.style.display = 'block';
        loadMaskImages();
    }

    function loadMaskImages() {
        fetch('/get_processed_images')
            .then(response => response.json())
            .then(data => {
                maskImages = data.images;
                if (maskImages.length > 0) {
                    loadMaskImage(0);
                } else {
                    statusMessage.textContent = "Nenhuma imagem processada encontrada.";
                }
            })
            .catch(error => {
                console.error("Erro ao carregar imagens:", error);
                statusMessage.textContent = "Erro ao carregar imagens.";
            });
    }

    function loadMaskImage(index) {
        if (index >= 0 && index < maskImages.length) {
            currentMaskIndex = index;
            maskImage.src = '/processed/' + maskImages[index];
            maskImage.onload = function() {
                console.log('Image fully loaded');
                setTimeout(resetRectangles, 0);
            };
        }
    }

    function resetRectangles() {
        const containerRect = maskImage.getBoundingClientRect();

        console.log('Resetting rectangles');
        console.log('Container rect:', containerRect);

        maskRectBlue.style.left = '10px';
        maskRectBlue.style.top = '10px';
        maskRectBlue.style.width = '100px';
        maskRectBlue.style.height = '100px';

        maskRect1.style.left = '120px';
        maskRect1.style.top = '10px';
        maskRect1.style.width = '50px';
        maskRect1.style.height = '50px';

        maskRect2.style.left = '180px';
        maskRect2.style.top = '70px';
        maskRect2.style.width = '50px';
        maskRect2.style.height = '50px';

        console.log('Rectangles reset');
        console.log('Blue rect position:', maskRectBlue.style.left, maskRectBlue.style.top);
        console.log('Blue rect size:', maskRectBlue.offsetWidth, maskRectBlue.offsetHeight);
        console.log('Red rect 1 size:', maskRect1.offsetWidth, maskRect1.offsetHeight);
        console.log('Red rect 2 size:', maskRect2.offsetWidth, maskRect2.offsetHeight);
    }

    function makeResizableAndDraggable(element) {
        let isResizing = false;
        let isDragging = false;
        let currentX;
        let currentY;
        let initialWidth;
        let initialHeight;

        element.addEventListener('mousedown', function(e) {
            if (e.offsetX > element.offsetWidth - 10 && e.offsetY > element.offsetHeight - 10) {
                isResizing = true;
            } else {
                isDragging = true;
            }
            currentX = e.clientX;
            currentY = e.clientY;
            initialWidth = parseFloat(getComputedStyle(this).getPropertyValue('width').slice(0, -2));
            initialHeight = parseFloat(getComputedStyle(this).getPropertyValue('height').slice(0, -2));
        });

        document.addEventListener('mousemove', function(e) {
            if (isResizing) {
                const width = initialWidth + (e.clientX - currentX);
                const height = initialHeight + (e.clientY - currentY);
                element.style.width = width + 'px';
                element.style.height = height + 'px';
            } else if (isDragging) {
                const dx = e.clientX - currentX;
                const dy = e.clientY - currentY;
                element.style.left = (element.offsetLeft + dx) + 'px';
                element.style.top = (element.offsetTop + dy) + 'px';
                currentX = e.clientX;
                currentY = e.clientY;
            }
        });

        document.addEventListener('mouseup', function() {
            isResizing = false;
            isDragging = false;
        });
    }

    makeResizableAndDraggable(maskRectBlue);
    makeResizableAndDraggable(maskRect1);
    makeResizableAndDraggable(maskRect2);

    applyMaskButton.addEventListener('click', function() {
        const imageRect = maskImage.getBoundingClientRect();
        const rectBlue = maskRectBlue.getBoundingClientRect();
        const rect1 = maskRect1.getBoundingClientRect();
        const rect2 = maskRect2.getBoundingClientRect();
    
        const data = {
            filename: maskImages[currentMaskIndex],
            rectBlue: {
                x: (rectBlue.left - imageRect.left) / imageRect.width,
                y: (rectBlue.top - imageRect.top) / imageRect.height,
                width: rectBlue.width / imageRect.width,
                height: rectBlue.height / imageRect.height
            },
            rect1: {
                x: (rect1.left - imageRect.left) / imageRect.width,
                y: (rect1.top - imageRect.top) / imageRect.height,
                width: rect1.width / imageRect.width,
                height: rect1.height / imageRect.height
            },
            rect2: {
                x: (rect2.left - imageRect.left) / imageRect.width,
                y: (rect2.top - imageRect.top) / imageRect.height,
                width: rect2.width / imageRect.width,
                height: rect2.height / imageRect.height
            }
        };
    
        fetch('/apply_mask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            console.log(result.message);
            statusMessage.textContent = result.message;
        })
        .catch(error => {
            console.error('Error:', error);
            statusMessage.textContent = 'Error applying mask';
        });
    });

    previousButtonMask.addEventListener('click', () => {
        if (currentMaskIndex > 0) {
            loadMaskImage(currentMaskIndex - 1);
        }
    });

    nextButtonMask.addEventListener('click', () => {
        if (currentMaskIndex < maskImages.length - 1) {
            loadMaskImage(currentMaskIndex + 1);
        }
    });

    function showSegmentationSection() {
        console.log("Botão Segmentation clicado");
        document.querySelectorAll('.section').forEach(section => {
            section.style.display = 'none';
        });
        segmentationSection.style.display = 'block';
        loadSegmentationImages();
    }

    function loadSegmentationImages() {
        console.log("Carregando imagens de segmentação");
        fetch('/get_processed_images')
            .then(response => response.json())
            .then(data => {
                segmentationImages = data.images;
                console.log("Imagens carregadas:", segmentationImages);
                if (segmentationImages.length > 0) {
                    loadSegmentationImage(0);
                } else {
                    console.log("Nenhuma imagem processada encontrada.");
                    statusMessage.textContent = "Nenhuma imagem processada encontrada.";
                }
            })
            .catch(error => {
                console.error("Erro ao carregar imagens:", error);
                statusMessage.textContent = "Erro ao carregar imagens.";
            });
    }

    showSegmentationButton.addEventListener('click', showSegmentationSection);

    let frames = [];
    let currentFrameIndex = 0;
    let currentVideoFile = null;
    let videoDuration = 0;
    let cropCount = 0;
    let segmentationImages = [];
    let currentSegmentationIndex = 0;

    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }

    // Drag and drop functionality
    dropArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropArea.style.backgroundColor = '#e9e9e9';
    });

    dropArea.addEventListener('dragleave', () => {
        dropArea.style.backgroundColor = '';
    });

    dropArea.addEventListener('drop', (e) => {
        e.preventDefault();
        dropArea.style.backgroundColor = '';
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('video/')) {
            handleVideoUpload(file);
        }
    });

    uploadButton.addEventListener('click', () => videoInput.click());

    videoInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            handleVideoUpload(file);
        }
    });

    function handleVideoUpload(file) {
        const formData = new FormData();
        formData.append('file', file);
    
        const loadingInterval = animateLoadingText('statusMessage', 'Uploading video');
    
        fetch('/upload_video', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            clearInterval(loadingInterval);
            if (data.error) {
                statusMessage.textContent = data.error;
            } else {
                currentVideoFile = data.filename;
                videoDuration = data.duration;
                initializeTimeSlider();
                uploadSection.style.display = 'none';
                configSection.style.display = 'block';
                statusMessage.textContent = '';
            }
        })
        .catch(error => {
            clearInterval(loadingInterval);
            statusMessage.textContent = 'Error uploading video: ' + error;
        });
    }

    function initializeTimeSlider() {
        $("#timeSlider").slider({
            range: true,
            min: 0,
            max: videoDuration,
            values: [0, videoDuration],
            slide: function(event, ui) {
                $("#startTimeValue").text(formatTime(ui.values[0]));
                $("#endTimeValue").text(formatTime(ui.values[1]));
            }
        });
        $("#startTimeValue").text(formatTime(0));
        $("#endTimeValue").text(formatTime(videoDuration));
    }

    fragmentButton.addEventListener('click', () => {
        configSection.style.display = 'none';
        cropSection.style.display = 'block';
        loadUploadedImages();
    });

    function loadUploadedImages() {
        fetch('/get_uploaded_images')
            .then(response => response.json())
            .then(data => {
                uploadedImages = data.images;
                if (uploadedImages.length > 0) {
                    loadImage(0);
                } else {
                    statusMessage.textContent = "No uploaded images found.";
                }
            })
            .catch(error => {
                console.error("Error loading images:", error);
                statusMessage.textContent = "Error loading images.";
            });
    }

    maskImage.addEventListener('load', function() {
        console.log('Image fully loaded');
        resetRectangles();
    });

    function loadImage(index) {
        if (index >= 0 && index < uploadedImages.length) {
            currentImageIndex = index;
            image.src = '/uploads/' + uploadedImages[index];

            image.onload = function() {
                const containerWidth = 600;
                const containerHeight = 400;
                
                const originalWidth = image.naturalWidth;
                const originalHeight = image.naturalHeight;
                
                const scale = Math.min(containerWidth / originalWidth, containerHeight / originalHeight);
                
                const scaledWidth = originalWidth * scale;
                const scaledHeight = originalHeight * scale;
                
                image.style.width = `${scaledWidth}px`;
                image.style.height = `${scaledHeight}px`;

                const frameSize = document.getElementById('frameSize').value;
                const scaledFrameSize = frameSize * scale;
                
                cropArea.style.width = `${scaledFrameSize}px`;
                cropArea.style.height = `${scaledFrameSize}px`;
                cropArea.style.left = '0px';
                cropArea.style.top = '0px';

                // Store original dimensions and scale for use in cropping
                image.dataset.originalWidth = originalWidth;
                image.dataset.originalHeight = originalHeight;
                image.dataset.scale = scale;
            };
        }
    }

    previousButton.addEventListener('click', () => {
        if (currentImageIndex > 0) {
            loadImage(currentImageIndex - 1);
        }
    });

    nextButton.addEventListener('click', () => {
        if (currentImageIndex < uploadedImages.length - 1) {
            loadImage(currentImageIndex + 1);
        }
    });

    cropButton.addEventListener('click', () => {
        const rect = cropArea.getBoundingClientRect();
        const imageRect = image.getBoundingClientRect();
    
        const scale = parseFloat(image.dataset.scale);
        const originalWidth = parseInt(image.dataset.originalWidth);
        const originalHeight = parseInt(image.dataset.originalHeight);
    
        const x = (rect.left - imageRect.left) / scale;
        const y = (rect.top - imageRect.top) / scale;
        const width = rect.width / scale;
        const height = rect.height / scale;
    
        fetch('/crop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                filename: uploadedImages[currentImageIndex],
                x: x,
                y: y,
                width: width,
                height: height,
                originalWidth: originalWidth,
                originalHeight: originalHeight
            }),
        })
        .then(response => response.json())
        .then(data => {
            statusMessage.textContent = data.message;
            cropCount++;
            cropCountElement.textContent = `Cropped images: ${cropCount}`;
            if (currentImageIndex < uploadedImages.length - 1) {
                loadImage(currentImageIndex + 1);
            }
        })
        .catch(error => {
            statusMessage.textContent = 'Error cropping image: ' + error;
        });
    });

    function animateLoadingText(elementId, baseText) {
        let dots = 0;
        return setInterval(() => {
            const element = document.getElementById(elementId);
            dots = (dots + 1) % 4;
            element.textContent = baseText + '.'.repeat(dots);
        }, 500);
    }

    function loadFrame(index) {
        if (index >= 0 && index < frames.length) {
            currentFrameIndex = index;
            image.src = '/frames/' + frames[index];
    
            image.onload = function() {
                const containerWidth = 600;
                const containerHeight = 400;
                
                const originalWidth = image.naturalWidth;
                const originalHeight = image.naturalHeight;
                
                const scale = Math.min(containerWidth / originalWidth, containerHeight / originalHeight);
                
                const scaledWidth = originalWidth * scale;
                const scaledHeight = originalHeight * scale;
                
                image.style.width = `${scaledWidth}px`;
                image.style.height = `${scaledHeight}px`;
    
                const frameSize = document.getElementById('frameSize').value;
                const scaledFrameSize = frameSize * scale;
                
                cropArea.style.width = `${scaledFrameSize}px`;
                cropArea.style.height = `${scaledFrameSize}px`;
                cropArea.style.left = '0px';
                cropArea.style.top = '0px';
    
                // Store original dimensions and scale for use in cropping
                image.dataset.originalWidth = originalWidth;
                image.dataset.originalHeight = originalHeight;
                image.dataset.scale = scale;
            };
        }
    }

    previousButton.addEventListener('click', () => {
        if (currentFrameIndex > 0) {
            loadFrame(currentFrameIndex - 1);
        }
    });

    nextButton.addEventListener('click', () => {
        if (currentFrameIndex < frames.length - 1) {
            loadFrame(currentFrameIndex + 1);
        }
    });

    document.getElementById('brushSize').addEventListener('input', function() {
        document.getElementById('brushSizeValue').textContent = this.value;
    });

    cropButton.addEventListener('click', () => {
        const rect = cropArea.getBoundingClientRect();
        const imageRect = image.getBoundingClientRect();
    
        const scale = parseFloat(image.dataset.scale);
        const originalWidth = parseInt(image.dataset.originalWidth);
        const originalHeight = parseInt(image.dataset.originalHeight);
    
        const x = (rect.left - imageRect.left) / scale;
        const y = (rect.top - imageRect.top) / scale;
        const width = rect.width / scale;
        const height = rect.height / scale;
    
        fetch('/crop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                filename: frames[currentFrameIndex],
                x: x,
                y: y,
                width: width,
                height: height,
                originalWidth: originalWidth,
                originalHeight: originalHeight
            }),
        })
        .then(response => response.json())
        .then(data => {
            statusMessage.textContent = data.message;
            cropCount++;
            cropCountElement.textContent = `Cropped images: ${cropCount}`;
            if (currentFrameIndex < frames.length - 1) {
                loadFrame(currentFrameIndex + 1);
            }
        })
        .catch(error => {
            statusMessage.textContent = 'Error cropping image: ' + error;
        });
    });

    // Make crop area draggable and resizable
    let isDragging = false;
    let isResizing = false;
    let startX, startY, startWidth, startHeight;

    cropArea.addEventListener('mousedown', (e) => {
        if (e.target === cropArea) {
            isDragging = true;
        } else {
            isResizing = true;
        }
        startX = e.clientX - cropArea.offsetLeft;
        startY = e.clientY - cropArea.offsetTop;
        startWidth = parseInt(getComputedStyle(cropArea).width, 10);
        startHeight = parseInt(getComputedStyle(cropArea).height, 10);
    });

    document.addEventListener('mousemove', (e) => {
        if (isDragging) {
            const newLeft = e.clientX - startX;
            const newTop = e.clientY - startY;
            cropArea.style.left = `${newLeft}px`;
            cropArea.style.top = `${newTop}px`;
        } else if (isResizing) {
            const newWidth = startWidth + (e.clientX - (startX + cropArea.offsetLeft));
            const newHeight = startHeight + (e.clientY - (startY + cropArea.offsetTop));
            cropArea.style.width = `${newWidth}px`;
            cropArea.style.height = `${newHeight}px`;
        }
    });

    document.addEventListener('mouseup', () => {
        isDragging = false;
        isResizing = false;
    });

    function loadSegmentationImage(index) {
        if (index >= 0 && index < segmentationImages.length) {
            currentSegmentationIndex = index;
            const img = new Image();
            img.onload = function() {
                const containerWidth = 600;
                const containerHeight = 400;
                
                const originalWidth = img.naturalWidth;
                const originalHeight = img.naturalHeight;
                
                const scale = Math.min(containerWidth / originalWidth, containerHeight / originalHeight);
                
                const scaledWidth = originalWidth * scale;
                const scaledHeight = originalHeight * scale;
                
                segmentationCanvas.width = scaledWidth;
                segmentationCanvas.height = scaledHeight;
                const ctx = segmentationCanvas.getContext('2d');
                ctx.drawImage(img, 0, 0, scaledWidth, scaledHeight);
    
                // Store original dimensions and scale for use in segmentation
                segmentationCanvas.dataset.originalWidth = originalWidth;
                segmentationCanvas.dataset.originalHeight = originalHeight;
                segmentationCanvas.dataset.scale = scale;
            };
            img.src = '/processed/' + segmentationImages[index];
        }
    }

    let isDrawing = false;
    let lastX = 0;
    let lastY = 0;

    segmentationCanvas.addEventListener('mousedown', startDrawing);
    segmentationCanvas.addEventListener('mousemove', draw);
    segmentationCanvas.addEventListener('mouseup', stopDrawing);
    segmentationCanvas.addEventListener('mouseout', stopDrawing);

    function startDrawing(e) {
        isDrawing = true;
        [lastX, lastY] = [e.offsetX, e.offsetY];
    }

    function draw(e) {
        if (!isDrawing) return;
        const ctx = segmentationCanvas.getContext('2d');
        ctx.beginPath();
        ctx.moveTo(lastX, lastY);
        ctx.lineTo(e.offsetX, e.offsetY);
        ctx.strokeStyle = 'red';
        ctx.lineWidth = document.getElementById('brushSize').value;
        ctx.lineCap = 'round';
        ctx.stroke();
        [lastX, lastY] = [e.offsetX, e.offsetY];
    }

    function stopDrawing() {
        isDrawing = false;
    }

    previousButtonSegmentation.addEventListener('click', () => {
        if (currentSegmentationIndex > 0) {
            loadSegmentationImage(currentSegmentationIndex - 1);
        }
    });

    nextButtonSegmentation.addEventListener('click', () => {
        if (currentSegmentationIndex < segmentationImages.length - 1) {
            loadSegmentationImage(currentSegmentationIndex + 1);
        }
    });

    applySegmentationButton.addEventListener('click', () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const originalWidth = parseInt(segmentationCanvas.dataset.originalWidth);
        const originalHeight = parseInt(segmentationCanvas.dataset.originalHeight);
        
        canvas.width = originalWidth;
        canvas.height = originalHeight;
        
        ctx.drawImage(segmentationCanvas, 0, 0, originalWidth, originalHeight);
        
        const imageData = canvas.toDataURL('image/png');
        fetch('/apply_segmentation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                image: imageData,
                filename: segmentationImages[currentSegmentationIndex],
                originalWidth: originalWidth,
                originalHeight: originalHeight
            }),
        })
        .then(response => response.json())
        .then(data => {
            statusMessage.textContent = data.message;
        });
    });
});
