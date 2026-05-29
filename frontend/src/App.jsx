import { useCallback, useEffect, useRef, useState } from "react";
import "./App.css";

const API_BASE = "/api";
const POLL_MS = 2000;
const ALLOWED = [".mp4", ".avi", ".mov", ".mkv", ".webm"];

export default function App() {
  const [file, setFile] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [modelOk, setModelOk] = useState(null);
  const inputRef = useRef(null);
  const pollRef = useRef(null);

  useEffect(() => {
    fetch(`${API_BASE}/health`)
      .then((r) => r.json())
      .then((d) => setModelOk(d.model_exists))
      .catch(() => setModelOk(false));
  }, []);

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  const pollJob = useCallback(
    (id) => {
      stopPolling();
      pollRef.current = setInterval(async () => {
        try {
          const res = await fetch(`${API_BASE}/jobs/${id}`);
          if (!res.ok) throw new Error("Impossible de récupérer le statut.");
          const data = await res.json();
          setStatus(data);
          if (data.state === "completed" || data.state === "failed") {
            stopPolling();
            if (data.state === "failed") {
              setError(data.error || "L'analyse a échoué.");
            }
          }
        } catch (e) {
          stopPolling();
          setError(e.message);
        }
      }, POLL_MS);
    },
    [stopPolling]
  );

  useEffect(() => () => stopPolling(), [stopPolling]);

  const pickFile = (f) => {
    if (!f) return;
    const ext = f.name.slice(f.name.lastIndexOf(".")).toLowerCase();
    if (!ALLOWED.includes(ext)) {
      setError(`Format non supporté. Utilisez : ${ALLOWED.join(", ")}`);
      return;
    }
    setError(null);
    setFile(f);
    setJobId(null);
    setStatus(null);
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (uploading || status?.state === "running") return;
    pickFile(e.dataTransfer.files?.[0]);
  };

  const startAnalysis = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);
    setStatus(null);
    setJobId(null);

    const form = new FormData();
    form.append("file", file);

    try {
      const res = await fetch(`${API_BASE}/jobs`, {
        method: "POST",
        body: form,
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.detail || "Erreur lors de l'envoi.");
      }
      setJobId(data.job_id);
      setStatus(data);
      pollJob(data.job_id);
    } catch (e) {
      setError(e.message);
    } finally {
      setUploading(false);
    }
  };

  const busy =
    uploading || status?.state === "running" || status?.state === "pending";
  const done = status?.state === "completed";
  const resultUrl = jobId ? `${API_BASE}/jobs/${jobId}/result` : null;

  return (
    <div className="app">
      <header className="header">
        <h1>Analyse Football</h1>
        <p>
          Uploadez un match, lancez la détection YOLO et récupérez la vidéo
          annotée (équipes, vitesse, distance, possession).
        </p>
        {modelOk === false && (
          <span className="badge warn">Modèle best.pt manquant sur le serveur</span>
        )}
        {modelOk === true && (
          <span className="badge ok">API prête</span>
        )}
      </header>

      <section className="card">
        <div
          className={`dropzone ${dragOver ? "dragover" : ""} ${busy ? "disabled" : ""}`}
          onDragOver={(e) => {
            e.preventDefault();
            if (!busy) setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={onDrop}
          onClick={() => !busy && inputRef.current?.click()}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => e.key === "Enter" && !busy && inputRef.current?.click()}
        >
          <input
            ref={inputRef}
            type="file"
            accept={ALLOWED.join(",")}
            onChange={(e) => pickFile(e.target.files?.[0])}
            disabled={busy}
          />
          <strong>Glissez une vidéo ici</strong>
          <span>ou cliquez pour choisir (.mp4, .avi, .mov… max 500 Mo)</span>
        </div>

        {file && <p className="file-name">Fichier : {file.name}</p>}

        <button
          className="btn"
          type="button"
          disabled={!file || busy || modelOk === false}
          onClick={startAnalysis}
        >
          {uploading ? "Envoi en cours…" : busy ? "Analyse en cours…" : "Lancer l'analyse"}
        </button>

        {(busy || done) && status && (
          <div className="progress-block">
            <div className="progress-label">
              <span>{status.message}</span>
              <span>{status.progress}%</span>
            </div>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${status.progress}%` }}
              />
            </div>
            <p className="status-message">État : {status.state}</p>
          </div>
        )}

        {error && <div className="error">{error}</div>}

        {done && resultUrl && (
          <div className="result">
            <h2>Résultat</h2>
            <video src={resultUrl} controls />
            <a className="download-link" href={resultUrl} download>
              Télécharger la vidéo annotée
            </a>
          </div>
        )}
      </section>
    </div>
  );
}
