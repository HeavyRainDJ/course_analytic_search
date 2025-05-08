import React, { useState } from 'react';
import Header from '../../components/Header/header';
import styles from './searchPage.module.css';

const Search = () => {
  const [channelUrl, setChannelUrl] = useState('');
  const [date, setDate] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [jsonData, setJsonData] = useState(null);
  const [processedJson, setProcessedJson] = useState(null);
  const isValidTelegramLink = (url) => {
    return /^(https?:\/\/)?t\.me\/[a-zA-Z0-9_]+\/?$/.test(url);
  };

  const handleParse = async () => {
    if (!isValidTelegramLink(channelUrl)) {
      alert('Ошибка! Введите корректную ссылку на Telegram-канал. Парсинг не запущен.');
      return;
    }

    setIsLoading(true);
    setJsonData(null);

    try {
      const response = await fetch('http://127.0.0.1:5000/tgstat_pipeline', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          start_date: date,
          tg_name: channelUrl
        })
      });

      if (!response.ok) {
        throw new Error('Ошибка при получении данных с сервера');
      }

      const data = await response.json();
      setJsonData(data);
    } catch (error) {
      alert(`Произошла ошибка: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handlejsonDownload = async (fileNumber) => {
    const tgName = channelUrl.split('/').pop();
  
    if (fileNumber === 1 && jsonData) {
      const fileContent = JSON.stringify(jsonData, null, 2);
      const blob = new Blob([fileContent], { type: 'application/json' });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = `tg_data_${tgName}_raw.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  
    if (fileNumber === 2) {
      try {
        const response = await fetch(`http://127.0.0.1:5000/get_processed_data?db_name=storage_processing&collection=${tgName}&start_date=${date}`);
        const data = await response.json();
        const fileContent = JSON.stringify(data, null, 2);
        const blob = new Blob([fileContent], { type: 'application/json' });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = `tg_data_${tgName}_vectors.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } catch (error) {
        alert("Ошибка при загрузке обработанных данных");
        console.error(error);
      }
    }
  };

  const handleGrafanaVisualization = () => {
    console.log("Открытие Grafana");
    window.location.href = "https://viktorloginovrain.grafana.net/d/tg_analytics_auto/telegram-analytics-auto?orgId=1&from=now-30d&to=now&timezone=browser&var-channel=$__all&refresh=10s";
  };

  return (
    <div className={styles.search_page}>
      <Header />
      <div className={styles.card}>
        <h2>Парсинг Telegram канала</h2>
        <input 
          type="text" 
          placeholder="Введите ссылку на канал"
          value={channelUrl} 
          onChange={(e) => {
            setChannelUrl(e.target.value);
            setJsonData(null);
          }}
          className={styles.input}
        />
        <input 
          type="date" 
          value={date} 
          onChange={(e) => setDate(e.target.value)}
          className={styles.input}
        />
        <button 
          onClick={handleParse} 
          disabled={isLoading || !channelUrl || !date}
          className={styles.button}>
          Подтвердить парсинг
        </button>
        {isLoading && <div className={styles.loader}></div>}
        {jsonData && (
          <>
            <button onClick={() => handlejsonDownload(1)} className={styles.button}>
              JSON-FILE-1
            </button>
            <button onClick={() => handlejsonDownload(2)} className={styles.button}>
              JSON-FILE-2
            </button>
            <button onClick={handleGrafanaVisualization} className={styles.grafana_button}>
              Grafana Visualization 
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default Search;
