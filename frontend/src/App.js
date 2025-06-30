import React, { useEffect, useState } from 'react';

function App() {
  const [data, setData] = useState([]);

  useEffect(() => {
    // Appel GET vers ton API Flask
    fetch('http://localhost:5000/api/data')
      .then(response => response.json())
      .then(json => setData(json))
      .catch(err => console.error('Erreur API:', err));
  }, []);

  return (
    <div>
      <h1>Données depuis Flask + MongoDB</h1>
      <ul>
        {data.length === 0 && <li>Aucune donnée</li>}
        {data.map((item, index) => (
          <li key={index}>
            {JSON.stringify(item)}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;

