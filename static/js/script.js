const videoFeed = document.getElementById('videoFeed');
        const volumeLevel = document.getElementById('volumeLevel');
        const volumeText = document.getElementById('volumeText');

        const ws = new WebSocket('ws://localhost:8000/ws');

        ws.onmessage = function(event) {
            if (event.data instanceof Blob) {
                // Handle video frame
                const urlObject = URL.createObjectURL(event.data);
                videoFeed.src = urlObject;
            } else {
                // Handle JSON data (volume and hand position)
                const data = JSON.parse(event.data);
                updateVolumeDisplay(data.volume);
                drawHandPosition(data);
            }
        };

        function updateVolumeDisplay(volume) {
            volumeLevel.style.height = `${volume}%`;
            volumeText.textContent = `Volume: ${volume}%`;
        }

        function drawHandPosition(data) {
            const ctx = videoFeed.getContext('2d');
            ctx.beginPath();
            ctx.moveTo(data.thumbX, data.thumbY);
            ctx.lineTo(data.indexX, data.indexY);
            ctx.strokeStyle = '#FF0000';
            ctx.lineWidth = 2;
            ctx.stroke();
        }