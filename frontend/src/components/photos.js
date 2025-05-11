import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./../styles/photos.css";

const Photos = () => {
  const [photos, setPhotos] = useState([]);
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState("");
  const [responseMessage, setResponseMessage] = useState(null);
  const navigate = useNavigate();

  const userId = localStorage.getItem("userId");

  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  useEffect(() => {
    const fetchPhotos = async () => {
      try {
        const response = await fetch(`http://localhost:5005/photos/${userId}`);
        const data = await response.json();
        if (response.ok) {
          setPhotos(data.photos || []);
        } else {
          console.error("Error fetching photos:", data.message);
          setResponseMessage({ type: "error", text: "No photos available." });
        }
      } catch (error) {
        console.error("Error fetching photos:", error);
        setResponseMessage({ type: "error", text: "Error fetching photos." });
      }
    };
    fetchPhotos();
  }, [userId]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setFileName(selectedFile ? selectedFile.name : "");
  };

  const handleUploadPhoto = async () => {
    if (!file) {
      setResponseMessage({
        type: "error",
        text: "Please select a photo file to upload.",
      });
      return;
    }

    const formData = new FormData();
    formData.append("photo", file);
    formData.append("user_id", userId);

    try {
      setResponseMessage({ text: "Uploading Photo..." });
      const response = await fetch("http://localhost:5007/photos/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setResponseMessage({
          type: "success",
          text: "Photo uploaded successfully!",
        });
        setFile(null);
        setFileName("");
        await sleep(2000);
        window.location.reload();
      } else {
        console.error("Upload failed:", data.message);
        setResponseMessage({
          type: "error",
          text: "Cannot upload photo, daily bandwidth or storage will exceed.",
        });
      }
    } catch (error) {
      console.error("Upload error:", error);
      setResponseMessage({ type: "error", text: "Error uploading photo." });
    }
  };

  const handleDeletePhoto = async (photoName) => {
    const confirmDelete = window.confirm(
      "Are you sure you want to delete this photo?"
    );
    if (!confirmDelete) return;

    try {
      const response = await fetch(
        `http://localhost:5006/photos/delete/${photoName}?user_id=${userId}`,
        {
          method: "DELETE",
        }
      );
      const data = await response.json();
      if (response.ok) {
        setResponseMessage({
          type: "success",
          text: "Photo deleted successfully!",
        });
        await sleep(2000);
        window.location.reload();
      } else {
        console.error("Delete failed:", data.message);
        setResponseMessage({ type: "error", text: "Error deleting photo." });
      }
    } catch (error) {
      console.error("Delete error:", error);
      setResponseMessage({ type: "error", text: "Error deleting photo." });
    }
  };

  return (
    <div className="photos-container">
      <button className="navigate-button" onClick={() => navigate("/dashboard")}>
        Back
      </button>
      <h2>Photo Gallery</h2>

      {responseMessage && (
        <div className={`response-message ${responseMessage.type}`}>
          {responseMessage.text}
        </div>
      )}

      <div className="upload-section">
        <h3>Upload Photo</h3>
        <label htmlFor="photo-upload" className="custom-file-label">
          Choose a photo
        </label>
        <input
          type="file"
          id="photo-upload"
          accept=".jpg, .jpeg, .png, .gif"
          onChange={handleFileChange}
          style={{ display: "none" }}
        />
        <button onClick={handleUploadPhoto}>Upload Photo</button>
        {fileName && <p>Selected Photo: {fileName}</p>}
      </div>

      <div className="photo-grid">
        {photos.length === 0 ? (
          <p>No photos available.</p>
        ) : (
          photos.map((photo, index) => (
            <div key={`${photo.name}-${index}`} className="photo-item">
              <img
                src={`data:image/jpeg;base64,${photo.content}`}
                alt={photo.name}
                className="photo-preview"
              />
              <div className="photo-name">{photo.name}</div>
              <button
                className="delete-photo-button"
                onClick={() => handleDeletePhoto(photo.name)}
              >
                Delete
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Photos;
