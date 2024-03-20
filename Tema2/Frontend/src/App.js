import React, { useState } from 'react';
import './App.css';

function App() {
  const [coverInfo, setCoverInfo] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  const fetchRandomCover = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/random_data/');
      const data = await response.json();

      if (!isValidData(data)) {
        setErrorMessage('Received JSON has unexpected structure.');
        setCoverInfo(null);
        return;
      }

      setCoverInfo(data);
      setErrorMessage(null);
    } catch (error) {
      console.error('Error fetching cover info:', error);
      setErrorMessage('Error fetching cover info.');
    }
  };

  const isValidData = (data) => {
    return (
      data &&
      data.spotify_song &&
      data.spotify_song.track_name &&
      data.spotify_song.artists &&
      data.guitar &&
      data.guitar.type &&
      data.guitar.brand &&
      data.photo &&
      data.photo.photo_url
    );
  };

  return (
    <div className="App">
      <h1>Random Guitar Cover Generator</h1>
      <button onClick={fetchRandomCover}>Give me a cover idea</button>
      {errorMessage && <p className="error">{errorMessage}</p>}
      {coverInfo && (
        <div className="coverInfo">
          <p>
            You will have to cover <strong>{coverInfo.spotify_song.track_name}</strong>, written by{' '}
            <strong>{coverInfo.spotify_song.artists}</strong>, using a {' '}
            <strong>{coverInfo.guitar.brand} {coverInfo.guitar.type}</strong> guitar and while being inspired by
            this image:
          </p>
          <img src={coverInfo.photo.photo_url} alt="Cover inspiration" />
        </div>
      )}
    </div>
  );
}

export default App;

