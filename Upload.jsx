import React from 'react';
import styled from 'styled-components';
import axios from 'axios';
import { FaCloudUploadAlt, FaSpinner } from 'react-icons/fa';

/* ===================== STYLES ===================== */

const Wrapper = styled.div`
  width: 100%;
  display: flex;
  justify-content: center;
  padding: 2rem 1rem;
`;

const UploadCard = styled.div`
  background: rgba(255, 255, 255, 0.25);
  padding: 3rem;
  border-radius: 20px;
  box-shadow: 0px 8px 25px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
  width: 100%;
  max-width: 600px;
  text-align: center;
  border: 2px dashed var(--secondary);
  transition: 0.3s ease-in-out;

  &:hover {
    border-color: var(--primary);
    transform: translateY(-3px);
  }
`;

const HiddenInput = styled.input`
  display: none;
`;

const UploadLabel = styled.label`
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;

  svg {
    font-size: 4rem;
    color: var(--secondary);
    margin-bottom: 1rem;
    transition: all 0.3s;
  }

  &:hover svg {
    color: var(--primary);
    transform: scale(1.08);
  }
`;

const UploadText = styled.p`
  font-size: 1.2rem;
  color: var(--text);
  font-weight: 500;
  opacity: 0.9;
`;

const Spinner = styled(FaSpinner)`
  animation: spin 1s linear infinite;
  font-size: 3rem;
  color: var(--primary);
  margin-bottom: 1rem;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

/* =====================================================
   LEAF DETECTION (DEFICIENCY-FRIENDLY)
   ===================================================== */

function isLeafImage(imageData) {
  const data = imageData.data;
  const totalPixels = imageData.width * imageData.height;
  let leafPixels = 0;

  for (let i = 0; i < data.length; i += 4) {
    const r = data[i];
    const g = data[i + 1];
    const b = data[i + 2];

    if (r > 240 && g > 240 && b > 240) continue;
    if (r < 30 && g < 30 && b < 30) continue;

    const isGreen = g > r && g > b;
    const isYellow = r > 150 && g > 150 && b < 120;
    const isPale = g > 120 && r > 120 && b < 160;

    if (isGreen || isYellow || isPale) leafPixels++;
  }

  return (leafPixels / totalPixels) > 0.08;
}

/* ===================== COMPONENT ===================== */

function Upload({ setResult, setLoading, loading }) {

  const uploadToBackend = async (file) => {
    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(
        "http://localhost:8000/predict",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      const previewUrl = URL.createObjectURL(file);
     setResult({
  ...response.data,
  previewUrl,
  file // ⭐ VERY IMPORTANT
});


    } catch (error) {
      console.error("Upload Error:", error);
      alert("Backend error! Make sure backend is running.");
    } finally {
      setLoading(false);

      // ✅ SAFE RESET (NO CRASH)
      const input = document.getElementById("leaf-upload");
      if (input) {
        input.value = null;
      }
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      alert("Please upload an image file.");
      e.target.value = null;
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      alert("Image too large! Max size is 5MB.");
      e.target.value = null;
      return;
    }

    const img = new Image();
    img.src = URL.createObjectURL(file);

    img.onload = () => {
      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d");

      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);

      const imageData = ctx.getImageData(0, 0, img.width, img.height);

      if (!isLeafImage(imageData)) {
        alert("Leaf not clearly detected. Please upload a clear leaf image.");
        e.target.value = null;
        return;
      }

      uploadToBackend(file);
    };
  };

  return (
    <Wrapper>
      <UploadCard>
        {loading ? (
          <div>
            <Spinner />
            <UploadText>Analyzing Leaf...</UploadText>
          </div>
        ) : (
          <>
            <HiddenInput
              type="file"
              id="leaf-upload"
              accept="image/*"
              onChange={handleFileChange}
            />
            <UploadLabel htmlFor="leaf-upload">
              <FaCloudUploadAlt />
              <UploadText>Click to Upload Leaf Image</UploadText>
            </UploadLabel>
          </>
        )}
      </UploadCard>
    </Wrapper>
  );
}

export default Upload;
