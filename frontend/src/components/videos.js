import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import "./../styles/videos.css"; // Import the CSS file

const Videos = () => {
  const [videoNames, setVideoNames] = useState([]); // Store video names
  const [selectedVideo, setSelectedVideo] = useState(null); // Store selected video details
  const [playingVideoId, setPlayingVideoId] = useState(null); // Store currently playing video ID
  const [file, setFile] = useState(null); // Store file for video upload
  const [responseMessage, setResponseMessage] = useState(null); // Store response messages for UI
  const [fileName, setFileName] = useState(""); // Store the name of the selected file
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const videoRef = useRef(null); // Reference to the video player
  const navigate = useNavigate(); // For navigation

  const userId = localStorage.getItem("userId");

  // Fetch video names on component mount
  useEffect(() => {
    const fetchVideoNames = async () => {
      try {
        const response = await fetch(
          `http://localhost:5008/videos/names/${userId}`
        );
        const data = await response.json();
        console.log("data: ", data);

        if (response.ok) {
          setVideoNames(data.video_metadata || []); // Save video names in state
        } else {
          console.error("Error fetching video names:", data.message);
          setResponseMessage({ type: "error", text: "No Videos Yet." });
        }
      } catch (error) {
        console.error("Error fetching video names:", error);
        setResponseMessage({ type: "error", text: "No videos yet." });
      }
    };
    fetchVideoNames();
  }, []);

  // Fetch specific video details when a video is clicked
  const handleVideoSelect = async (videoId) => {
    try {
      console.log(`Fetching video with ID: ${videoId}`);
      const response = await fetch(
        `http://localhost:5008/videos/${videoId}`
      );
      const data = await response.json();
      if (response.ok) {
        console.log("Video fetched successfully:", data);
        setSelectedVideo({
          id: videoId,
          url: data.video_data, // Update with the base64 video data
          title:
            videoNames.find((v) => v.id === videoId)?.upload_name || "Untitled",
        });
        setResponseMessage({
          type: "success",
          text: "Video loaded successfully.",
        });
      } else {
        console.error("Error fetching video:", data.message);
        setResponseMessage({ type: "error", text: "Error loading video." });
      }
    } catch (error) {
      console.error("Error fetching video:", error);
      setResponseMessage({ type: "error", text: "Error loading video." });
    }
  };

  // Handle play/pause video
  const handlePlayPause = () => {
    if (videoRef.current) {
      if (playingVideoId === selectedVideo.id) {
        console.log("Pausing video...");
        videoRef.current.pause();
        setPlayingVideoId(null);
      } else {
        console.log("Playing video...");
        videoRef.current.play();
        setPlayingVideoId(selectedVideo.id);
      }
    }
  };

  // Handle file input for video upload
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setFileName(selectedFile ? selectedFile.name : "");
  };

  // Upload video to the server
  const handleUploadVideo = async () => {
    if (!file) {
      setResponseMessage({
        type: "error",
        text: "Please select a video file to upload.",
      });
      return;
    }

    const formData = new FormData();
    formData.append("video", file);
    formData.append("user_id", userId);

    try {
      setResponseMessage({
        text: "Uploading Video.....",
      });
      const response = await fetch(
        "http://localhost:5000/videos/upload",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (response.ok) {
        console.log("Video uploaded successfully:", data);
        setResponseMessage({
          type: "success",
          text: "Video uploaded successfully!",
        });
        setFile(null); // Clear file input after upload
        setFileName("");
        await sleep(2000); // 2-second delay
        window.location.reload();
      } else {
        console.error("Error uploading video:", data.message);
        setResponseMessage({
          type: "error",
          text: "Cannot upload video, daily bandwidth or storage will exceed.",
        });
      }
    } catch (error) {
      console.error("Error uploading video:", error);
      setResponseMessage({ type: "error", text: "Error uploading video." });
    }
  };

  // Handle video deletion
  const handleDeleteVideo = async (videoId) => {
    const confirmDelete = window.confirm(
      "Are you sure you want to delete this video?"
    );
    if (!confirmDelete) return;

    try {
      console.log("userid", userId);
      const response = await fetch(
        `http://localhost:5009/videos/delete/${videoId}?user_id=${userId}`,
        {
          method: "DELETE",
        }
      );

      const data = await response.json();

      if (response.ok) {
        console.log("Video deleted successfully:", data);
        setResponseMessage({
          type: "success",
          text: "Video deleted successfully!",
        });
        // Delay before reloading
        await sleep(2000); // 2-second delay
        window.location.reload();
      } else {
        console.error("Error deleting video:", data.message);
        setResponseMessage({ type: "error", text: "Error deleting video." });
      }
    } catch (error) {
      console.error("Error deleting video:", error);
      setResponseMessage({ type: "error", text: "Error deleting video." });
    }
  };

  return (
    <div className="videos-container">
      <button
        className="navigate-button"
        onClick={() => navigate("/dashboard")}
      >
        Back
      </button>
      <h2>Video Gallery</h2>

      {/* Display Response Message */}
      {responseMessage && (
        <div className={`response-message ${responseMessage.type}`}>
          {responseMessage.text}
        </div>
      )}

      {/* Video Upload Section */}
      <div className="upload-section">
        <h3>Upload Video</h3>
        <label htmlFor="video-upload" className="custom-file-label">
          Choose a video
        </label>
        <input
          type="file"
          id="video-upload"
          accept=".mp4, .avi, .mov, .mkv" // Accept only specific video extensions
          onChange={handleFileChange}
          style={{ display: "none" }} // Hide the default input
        />
        <button onClick={handleUploadVideo}>Upload Video</button>
        {fileName && <p>Selected Video: {fileName}</p>}
      </div>

      {/* List of clickable video names */}
      <div className="video-names">
        {videoNames.map((video, index) => (
          <div key={`${video.id}-${index}`} className="video-item">
            <button
              className="video-name-button"
              onClick={() => handleVideoSelect(video.id)}
            >
              {video.upload_name}
            </button>
            <button
              className="delete-video-button"
              onClick={() => handleDeleteVideo(video.id)}
            >
              Delete
            </button>
          </div>
        ))}
      </div>

      {/* Selected video details */}
      {selectedVideo && (
        <div className="video-section">
  <div className="video-player-container">
    <h3>{selectedVideo.title}</h3>
    <video
      ref={videoRef}
      controls
      width="100%"
      src={`data:video/mp4;base64,${selectedVideo.url}`} // Set the src for the video
      onClick={handlePlayPause}
    >
      Your browser does not support the video tag.
    </video>
        </div>
        </div>
      )}
    </div>
  );
};

export default Videos;
