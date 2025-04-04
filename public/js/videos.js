import { html } from "./utils.js";

function createVideoHTML(options) {
    const videoHTML = html`
    <a href="/videotube/videos/${options.id}" class="flex flex-col gap-2 w-[300px] cursor-pointer rounded-xl p-2 group">
        <img
            width="300"
            height="168"
            class="rounded-xl object-cover border border-gray-300"
            src="${options.thumbnailURL}"
        />

        <div class="flex flex-row gap-3">
            <div class="flex flex-col">
                <h3 class="font-semibold text-base line-clamp-2 group-hover:underline">
                    ${options.title}
                </h3>
                <p class="text-sm text-gray-500 mt-1">Video Uploader</p>
                <div class="flex flex-row gap-1 text-sm text-gray-500">
                    <p>${options.created_at}</p>
                </div>
            </div>
        </div>
    </a>
  `;
    const videoElement = document.createElement("a");
    videoElement.innerHTML = videoHTML;

    return videoElement;
}

async function loadVideos() {
    try {
        const response = await fetch('/api/videos');
        if (!response.ok) {
            alertManager.newAlert(
                `Error: ${await response.text()}`,
                "error",
                5000,
                "Video Load Error"
            );
            return;
        }

        const data = await response.json();
        const videoList = document.getElementById("video-list");
        videoList.innerHTML = ''; // Clear mock data

        if (data.videos.length === 0) {
            videoList.innerHTML = '<p class="text-center text-gray-500">No videos found</p>';
            return;
        }

        data.videos.forEach((video) => {
            const videoHTML = createVideoHTML(video);
            videoList.appendChild(videoHTML);
        });
    } catch (error) {
        console.error('Error loading videos:', error);
        alertManager.newAlert(
            `Error: ${error.message}`,
            "error",
            5000,
            "Video Load Error"
        );
    }
}

loadVideos();
